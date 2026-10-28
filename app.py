from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "gymmanager-local-demo"
DB = Path(__file__).with_name("gymmanager.db")

def connect():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    return c

def init_db():
    with connect() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS customers(id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, phone TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS trainers(id INTEGER PRIMARY KEY, name TEXT NOT NULL, specialty TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS memberships(id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE, plan TEXT NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS classes(id INTEGER PRIMARY KEY, name TEXT NOT NULL, trainer_id INTEGER REFERENCES trainers(id) ON DELETE SET NULL, class_date TEXT NOT NULL, class_time TEXT NOT NULL, capacity INTEGER NOT NULL DEFAULT 10);
        CREATE TABLE IF NOT EXISTS bookings(id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE, class_id INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE, UNIQUE(customer_id,class_id));
        """)
        if c.execute("SELECT COUNT(*) FROM trainers").fetchone()[0] == 0:
            c.executemany("INSERT INTO trainers(name,specialty) VALUES (?,?)", [("Anna Kowalska","Trening siłowy"),("Marek Nowak","Fitness")])

@app.route("/")
def home():
    with connect() as c:
        stats = [c.execute("SELECT COUNT(*) FROM customers").fetchone()[0],
                 c.execute("SELECT COUNT(*) FROM memberships WHERE end_date >= date('now')").fetchone()[0],
                 c.execute("SELECT COUNT(*) FROM classes WHERE class_date >= date('now')").fetchone()[0],
                 c.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]]
        classes = c.execute("""SELECT cl.*, COALESCE(t.name,'Nie przypisano') trainer,
          COUNT(b.id) booked FROM classes cl LEFT JOIN trainers t ON t.id=cl.trainer_id
          LEFT JOIN bookings b ON b.class_id=cl.id GROUP BY cl.id ORDER BY cl.class_date,cl.class_time LIMIT 6""").fetchall()
    return render_template("home.html", stats=stats, classes=classes)

@app.route("/customers", methods=["GET","POST"])
def customers():
    with connect() as c:
        if request.method == "POST":
            name, email, phone = (request.form.get(x,"").strip() for x in ("name","email","phone"))
            if not name or not email: flash("Imię i e-mail są wymagane.","error")
            else:
                try:
                    c.execute("INSERT INTO customers(name,email,phone) VALUES (?,?,?)",(name,email,phone)); c.commit()
                    flash("Dodano klienta.","success"); return redirect(url_for("customers"))
                except sqlite3.IntegrityError: flash("Ten e-mail jest już w bazie.","error")
        rows = c.execute("SELECT * FROM customers ORDER BY name").fetchall()
    return render_template("customers.html", customers=rows)

@app.post("/customers/<int:id>/delete")
def delete_customer(id):
    with connect() as c: c.execute("DELETE FROM customers WHERE id=?",(id,)); c.commit()
    flash("Usunięto klienta.","success"); return redirect(url_for("customers"))

@app.route("/memberships", methods=["GET","POST"])
def memberships():
    with connect() as c:
        if request.method == "POST":
            cid=request.form.get("customer_id",type=int); plan=request.form.get("plan",""); start=request.form.get("start_date",""); end=request.form.get("end_date","")
            if not cid or not plan or not start or not end or end < start: flash("Sprawdź wymagane pola i daty.","error")
            else:
                c.execute("INSERT INTO memberships(customer_id,plan,start_date,end_date) VALUES (?,?,?,?)",(cid,plan,start,end)); c.commit()
                flash("Dodano karnet.","success"); return redirect(url_for("memberships"))
        people=c.execute("SELECT id,name FROM customers ORDER BY name").fetchall()
        rows=c.execute("""SELECT m.*,cu.name customer,CASE WHEN m.end_date>=date('now') THEN 'Aktywny' ELSE 'Wygasły' END status
        FROM memberships m JOIN customers cu ON cu.id=m.customer_id ORDER BY m.end_date DESC""").fetchall()
    return render_template("memberships.html", customers=people, memberships=rows)

@app.route("/trainers", methods=["GET","POST"])
def trainers():
    with connect() as c:
        if request.method == "POST":
            name=request.form.get("name","").strip(); specialty=request.form.get("specialty","").strip()
            if name: c.execute("INSERT INTO trainers(name,specialty) VALUES (?,?)",(name,specialty)); c.commit(); flash("Dodano trenera.","success"); return redirect(url_for("trainers"))
            flash("Imię i nazwisko jest wymagane.","error")
        rows=c.execute("SELECT * FROM trainers ORDER BY name").fetchall()
    return render_template("trainers.html", trainers=rows)

@app.route("/classes", methods=["GET","POST"])
def classes():
    with connect() as c:
        if request.method == "POST":
            name=request.form.get("name","").strip(); tid=request.form.get("trainer_id",type=int) or None
            date=request.form.get("class_date",""); time=request.form.get("class_time",""); cap=request.form.get("capacity",10,type=int)
            if not name or not date or not time or cap < 1: flash("Uzupełnij dane zajęć.","error")
            else:
                c.execute("INSERT INTO classes(name,trainer_id,class_date,class_time,capacity) VALUES (?,?,?,?,?)",(name,tid,date,time,cap)); c.commit()
                flash("Dodano zajęcia.","success"); return redirect(url_for("classes"))
        trainers=c.execute("SELECT * FROM trainers ORDER BY name").fetchall()
        people=c.execute("SELECT id,name FROM customers ORDER BY name").fetchall()
        rows=c.execute("""SELECT cl.*,COALESCE(t.name,'Nie przypisano') trainer,COUNT(b.id) booked
        FROM classes cl LEFT JOIN trainers t ON t.id=cl.trainer_id LEFT JOIN bookings b ON b.class_id=cl.id
        GROUP BY cl.id ORDER BY cl.class_date,cl.class_time""").fetchall()
    return render_template("classes.html", classes=rows, trainers=trainers, customers=people)

@app.post("/classes/<int:id>/book")
def book(id):
    cid=request.form.get("customer_id",type=int)
    with connect() as c:
        cl=c.execute("SELECT * FROM classes WHERE id=?",(id,)).fetchone()
        if not cl or not cid: flash("Wybierz klienta.","error")
        elif c.execute("SELECT 1 FROM bookings WHERE class_id=? AND customer_id=?",(id,cid)).fetchone(): flash("Klient jest już zapisany.","error")
        elif c.execute("SELECT COUNT(*) FROM bookings WHERE class_id=?",(id,)).fetchone()[0] >= cl["capacity"]: flash("Brak wolnych miejsc.","error")
        else: c.execute("INSERT INTO bookings(customer_id,class_id) VALUES (?,?)",(cid,id)); c.commit(); flash("Zapisano klienta.","success")
    return redirect(url_for("classes"))

@app.route("/bookings")
def bookings():
    with connect() as c:
        rows=c.execute("""SELECT cu.name customer,cl.name class_name,cl.class_date,cl.class_time
        FROM bookings b JOIN customers cu ON cu.id=b.customer_id JOIN classes cl ON cl.id=b.class_id
        ORDER BY cl.class_date,cl.class_time""").fetchall()
    return render_template("bookings.html", bookings=rows)

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5001, debug=False)

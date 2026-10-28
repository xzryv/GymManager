from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "gymmanager-secret"
DB = "gymmanager.db"


def connect_db():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def create_tables():
    db = connect_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT
    );

    CREATE TABLE IF NOT EXISTS trainers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        specialty TEXT
    );

    CREATE TABLE IF NOT EXISTS memberships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        plan TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        trainer_id INTEGER,
        class_date TEXT NOT NULL,
        class_time TEXT NOT NULL,
        capacity INTEGER NOT NULL,
        FOREIGN KEY(trainer_id) REFERENCES trainers(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        class_id INTEGER NOT NULL,
        UNIQUE(customer_id, class_id),
        FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE CASCADE,
        FOREIGN KEY(class_id) REFERENCES classes(id) ON DELETE CASCADE
    );
    """)
    if db.execute("SELECT COUNT(*) FROM trainers").fetchone()[0] == 0:
        db.execute("INSERT INTO trainers (name, specialty) VALUES (?, ?)",
                   ("Anna Kowalska", "Trening siłowy"))
        db.execute("INSERT INTO trainers (name, specialty) VALUES (?, ?)",
                   ("Marek Nowak", "Fitness"))
    db.commit()
    db.close()


@app.route("/")
def home():
    db = connect_db()
    customers_count = db.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    active_memberships = db.execute(
        "SELECT COUNT(*) FROM memberships WHERE start_date <= date('now') AND end_date >= date('now')"
    ).fetchone()[0]
    classes_count = db.execute(
        "SELECT COUNT(*) FROM classes WHERE class_date >= date('now')"
    ).fetchone()[0]
    bookings_count = db.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    classes = db.execute("""
        SELECT classes.*, trainers.name AS trainer,
        COUNT(bookings.id) AS booked
        FROM classes
        LEFT JOIN trainers ON classes.trainer_id = trainers.id
        LEFT JOIN bookings ON classes.id = bookings.class_id
        GROUP BY classes.id
        ORDER BY classes.class_date, classes.class_time
    """).fetchall()
    db.close()
    return render_template("home.html", customers_count=customers_count,
                           active_memberships=active_memberships,
                           classes_count=classes_count,
                           bookings_count=bookings_count, classes=classes)


@app.route("/customers", methods=["GET", "POST"])
def customers():
    db = connect_db()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        if name and email:
            try:
                db.execute("INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)",
                           (name, email, phone))
                db.commit()
                flash("Dodano klienta.")
                db.close()
                return redirect(url_for("customers"))
            except sqlite3.IntegrityError:
                flash("Klient z takim e-mailem już istnieje.")
        else:
            flash("Podaj imię, nazwisko i e-mail.")
    rows = db.execute("SELECT * FROM customers ORDER BY name").fetchall()
    db.close()
    return render_template("customers.html", customers=rows)


@app.route("/customers/<int:customer_id>/edit", methods=["GET", "POST"])
def edit_customer(customer_id):
    db = connect_db()
    customer = db.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
    if customer is None:
        db.close()
        flash("Nie znaleziono klienta.")
        return redirect(url_for("customers"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        if name and email:
            try:
                db.execute("UPDATE customers SET name = ?, email = ?, phone = ? WHERE id = ?",
                           (name, email, phone, customer_id))
                db.commit()
                db.close()
                flash("Zapisano zmiany.")
                return redirect(url_for("customers"))
            except sqlite3.IntegrityError:
                flash("Ten e-mail jest już używany.")
        else:
            flash("Imię i e-mail są wymagane.")
    db.close()
    return render_template("edit_customer.html", customer=customer)


@app.route("/customers/<int:customer_id>/delete", methods=["POST"])
def delete_customer(customer_id):
    db = connect_db()
    db.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
    db.commit()
    db.close()
    flash("Usunięto klienta.")
    return redirect(url_for("customers"))


@app.route("/memberships", methods=["GET", "POST"])
def memberships():
    db = connect_db()
    if request.method == "POST":
        customer_id = request.form.get("customer_id", type=int)
        plan = request.form.get("plan", "")
        start_date = request.form.get("start_date", "")
        end_date = request.form.get("end_date", "")
        if customer_id and plan and start_date and end_date and end_date >= start_date:
            db.execute("""INSERT INTO memberships
                (customer_id, plan, start_date, end_date) VALUES (?, ?, ?, ?)""",
                (customer_id, plan, start_date, end_date))
            db.commit()
            db.close()
            flash("Dodano karnet.")
            return redirect(url_for("memberships"))
        flash("Sprawdź dane i daty karnetu.")
    customers_list = db.execute("SELECT id, name FROM customers ORDER BY name").fetchall()
    rows = db.execute("""
        SELECT memberships.*, customers.name AS customer,
        CASE WHEN memberships.end_date >= date('now') THEN 'Aktywny' ELSE 'Wygasły' END AS status
        FROM memberships JOIN customers ON memberships.customer_id = customers.id
        ORDER BY memberships.end_date DESC
    """).fetchall()
    db.close()
    return render_template("memberships.html", customers=customers_list, memberships=rows)


@app.route("/trainers", methods=["GET", "POST"])
def trainers():
    db = connect_db()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        specialty = request.form.get("specialty", "").strip()
        if name:
            db.execute("INSERT INTO trainers (name, specialty) VALUES (?, ?)", (name, specialty))
            db.commit()
            db.close()
            flash("Dodano trenera.")
            return redirect(url_for("trainers"))
        flash("Podaj imię i nazwisko trenera.")
    rows = db.execute("SELECT * FROM trainers ORDER BY name").fetchall()
    db.close()
    return render_template("trainers.html", trainers=rows)


@app.route("/classes", methods=["GET", "POST"])
def classes():
    db = connect_db()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        trainer_id = request.form.get("trainer_id", type=int) or None
        class_date = request.form.get("class_date", "")
        class_time = request.form.get("class_time", "")
        capacity = request.form.get("capacity", 10, type=int)
        if name and class_date and class_time and capacity > 0:
            db.execute("""INSERT INTO classes
                (name, trainer_id, class_date, class_time, capacity)
                VALUES (?, ?, ?, ?, ?)""",
                (name, trainer_id, class_date, class_time, capacity))
            db.commit()
            db.close()
            flash("Dodano zajęcia.")
            return redirect(url_for("classes"))
        flash("Sprawdź dane zajęć.")
    trainers_list = db.execute("SELECT * FROM trainers ORDER BY name").fetchall()
    customers_list = db.execute("SELECT * FROM customers ORDER BY name").fetchall()
    rows = db.execute("""
        SELECT classes.*, trainers.name AS trainer, COUNT(bookings.id) AS booked
        FROM classes
        LEFT JOIN trainers ON classes.trainer_id = trainers.id
        LEFT JOIN bookings ON classes.id = bookings.class_id
        GROUP BY classes.id
        ORDER BY classes.class_date, classes.class_time
    """).fetchall()
    db.close()
    return render_template("classes.html", classes=rows, trainers=trainers_list,
                           customers=customers_list)


@app.route("/classes/<int:class_id>/book", methods=["POST"])
def book_class(class_id):
    customer_id = request.form.get("customer_id", type=int)
    db = connect_db()
    class_row = db.execute("SELECT * FROM classes WHERE id = ?", (class_id,)).fetchone()
    if class_row is None or customer_id is None:
        flash("Wybierz klienta.")
    else:
        count = db.execute("SELECT COUNT(*) FROM bookings WHERE class_id = ?",
                           (class_id,)).fetchone()[0]
        already_booked = db.execute(
            "SELECT id FROM bookings WHERE customer_id = ? AND class_id = ?",
            (customer_id, class_id)).fetchone()
        if already_booked:
            flash("Ten klient jest już zapisany.")
        elif count >= class_row["capacity"]:
            flash("Brak wolnych miejsc.")
        else:
            try:
                db.execute("INSERT INTO bookings (customer_id, class_id) VALUES (?, ?)",
                           (customer_id, class_id))
                db.commit()
                flash("Zapisano klienta na zajęcia.")
            except sqlite3.IntegrityError:
                flash("Nie udało się dodać zapisu.")
    db.close()
    return redirect(url_for("classes"))


@app.route("/bookings")
def bookings():
    db = connect_db()
    rows = db.execute("""
        SELECT customers.name AS customer, classes.name AS class_name,
        classes.class_date, classes.class_time
        FROM bookings
        JOIN customers ON bookings.customer_id = customers.id
        JOIN classes ON bookings.class_id = classes.id
        ORDER BY classes.class_date, classes.class_time
    """).fetchall()
    db.close()
    return render_template("bookings.html", bookings=rows)


if __name__ == "__main__":
    create_tables()
    app.run(host="127.0.0.1", port=5001, debug=False)

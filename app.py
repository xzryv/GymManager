import sqlite3
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox
from datetime import date

DB = Path(__file__).with_name("gymmanager.db")


def connect_db():
    db = sqlite3.connect(DB)
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
    db.commit()
    db.close()


class GymManager:
    def __init__(self, root):
        self.root = root
        self.root.title("GymManager - system siłowni")
        self.root.geometry("920x620")
        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)
        self.make_customers()
        self.make_memberships()
        self.make_trainers()
        self.make_classes()
        self.make_bookings()
        self.refresh_all()

    def make_table(self, tab, columns, labels):
        table = ttk.Treeview(tab, columns=columns, show="headings", height=13)
        for column, label in zip(columns, labels):
            table.heading(column, text=label)
            table.column(column, width=125)
        table.pack(fill="both", expand=True, pady=10)
        return table

    def make_customers(self):
        tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(tab, text="Klienci")
        form = ttk.Frame(tab)
        form.pack(fill="x")
        self.customer_name = tk.StringVar()
        self.customer_email = tk.StringVar()
        self.customer_phone = tk.StringVar()
        for label, value in [("Imię i nazwisko", self.customer_name), ("E-mail", self.customer_email), ("Telefon", self.customer_phone)]:
            ttk.Label(form, text=label).pack(side="left", padx=3)
            ttk.Entry(form, textvariable=value, width=17).pack(side="left", padx=3)
        ttk.Button(form, text="Dodaj", command=self.add_customer).pack(side="left", padx=3)
        ttk.Button(form, text="Zapisz edycję", command=self.edit_customer).pack(side="left", padx=3)
        ttk.Button(form, text="Usuń", command=self.delete_customer).pack(side="left", padx=3)
        self.customer_table = self.make_table(tab, ("id", "name", "email", "phone"), ("ID", "Imię i nazwisko", "E-mail", "Telefon"))
        self.customer_table.bind("<<TreeviewSelect>>", self.select_customer)

    def make_memberships(self):
        tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(tab, text="Karnety")
        form = ttk.Frame(tab)
        form.pack(fill="x")
        self.membership_customer = tk.StringVar()
        self.membership_plan = tk.StringVar(value="1 miesiąc")
        self.membership_start = tk.StringVar()
        self.membership_end = tk.StringVar()
        ttk.Label(form, text="Klient").pack(side="left", padx=3)
        self.customer_box = ttk.Combobox(form, textvariable=self.membership_customer, state="readonly", width=20)
        self.customer_box.pack(side="left", padx=3)
        ttk.Label(form, text="Rodzaj").pack(side="left", padx=3)
        ttk.Combobox(form, textvariable=self.membership_plan, values=("1 miesiąc", "3 miesiące", "12 miesięcy", "Jednorazowy"), state="readonly", width=14).pack(side="left", padx=3)
        ttk.Label(form, text="Od (RRRR-MM-DD)").pack(side="left", padx=3)
        ttk.Entry(form, textvariable=self.membership_start, width=12).pack(side="left", padx=3)
        ttk.Label(form, text="Do").pack(side="left", padx=3)
        ttk.Entry(form, textvariable=self.membership_end, width=12).pack(side="left", padx=3)
        ttk.Button(form, text="Dodaj karnet", command=self.add_membership).pack(side="left", padx=3)
        self.membership_table = self.make_table(tab, ("id", "customer", "plan", "start", "end", "status"), ("ID", "Klient", "Rodzaj", "Od", "Do", "Status"))

    def make_trainers(self):
        tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(tab, text="Trenerzy")
        form = ttk.Frame(tab)
        form.pack(fill="x")
        self.trainer_name = tk.StringVar()
        self.trainer_specialty = tk.StringVar()
        ttk.Label(form, text="Imię i nazwisko").pack(side="left", padx=3)
        ttk.Entry(form, textvariable=self.trainer_name, width=25).pack(side="left", padx=3)
        ttk.Label(form, text="Specjalizacja").pack(side="left", padx=3)
        ttk.Entry(form, textvariable=self.trainer_specialty, width=25).pack(side="left", padx=3)
        ttk.Button(form, text="Dodaj trenera", command=self.add_trainer).pack(side="left", padx=3)
        self.trainer_table = self.make_table(tab, ("id", "name", "specialty"), ("ID", "Imię i nazwisko", "Specjalizacja"))

    def make_classes(self):
        tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(tab, text="Zajęcia")
        form = ttk.Frame(tab)
        form.pack(fill="x")
        self.class_name = tk.StringVar()
        self.class_trainer = tk.StringVar()
        self.class_date = tk.StringVar()
        self.class_time = tk.StringVar()
        self.class_capacity = tk.StringVar(value="10")
        fields = [("Nazwa", self.class_name, 14), ("ID trenera", self.class_trainer, 9), ("Data RRRR-MM-DD", self.class_date, 14), ("Godzina", self.class_time, 9), ("Limit", self.class_capacity, 7)]
        for label, value, width in fields:
            ttk.Label(form, text=label).pack(side="left", padx=2)
            ttk.Entry(form, textvariable=value, width=width).pack(side="left", padx=2)
        ttk.Button(form, text="Dodaj zajęcia", command=self.add_class).pack(side="left", padx=3)
        self.class_table = self.make_table(tab, ("id", "name", "trainer", "date", "time", "capacity", "booked"), ("ID", "Zajęcia", "Trener", "Data", "Godzina", "Limit", "Zapisy"))

    def make_bookings(self):
        tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(tab, text="Zapisy")
        form = ttk.Frame(tab)
        form.pack(fill="x")
        self.booking_customer = tk.StringVar()
        self.booking_class = tk.StringVar()
        ttk.Label(form, text="ID klienta").pack(side="left", padx=3)
        ttk.Entry(form, textvariable=self.booking_customer, width=12).pack(side="left", padx=3)
        ttk.Label(form, text="ID zajęć").pack(side="left", padx=3)
        ttk.Entry(form, textvariable=self.booking_class, width=12).pack(side="left", padx=3)
        ttk.Button(form, text="Zapisz klienta", command=self.add_booking).pack(side="left", padx=3)
        self.booking_table = self.make_table(tab, ("id", "customer", "class", "date", "time"), ("ID", "Klient", "Zajęcia", "Data", "Godzina"))

    def fill_table(self, table, rows):
        for item in table.get_children():
            table.delete(item)
        for row in rows:
            table.insert("", "end", values=row)

    def refresh_all(self):
        db = connect_db()
        customers = db.execute("SELECT id, name, email, phone FROM customers ORDER BY name").fetchall()
        trainers = db.execute("SELECT id, name, specialty FROM trainers ORDER BY name").fetchall()
        memberships = db.execute("SELECT memberships.id, customers.name, memberships.plan, memberships.start_date, memberships.end_date, CASE WHEN memberships.start_date > date('now') THEN 'Zaplanowany' WHEN memberships.end_date >= date('now') THEN 'Aktywny' ELSE 'Wygasły' END FROM memberships JOIN customers ON customers.id = memberships.customer_id ORDER BY memberships.end_date DESC").fetchall()
        classes = db.execute("SELECT classes.id, classes.name, COALESCE(trainers.name, ''), classes.class_date, classes.class_time, classes.capacity, COUNT(bookings.id) FROM classes LEFT JOIN trainers ON trainers.id = classes.trainer_id LEFT JOIN bookings ON bookings.class_id = classes.id GROUP BY classes.id ORDER BY classes.class_date, classes.class_time").fetchall()
        bookings = db.execute("SELECT bookings.id, customers.name, classes.name, classes.class_date, classes.class_time FROM bookings JOIN customers ON customers.id = bookings.customer_id JOIN classes ON classes.id = bookings.class_id ORDER BY classes.class_date, classes.class_time").fetchall()
        db.close()
        self.fill_table(self.customer_table, customers)
        self.fill_table(self.trainer_table, trainers)
        self.fill_table(self.membership_table, memberships)
        self.fill_table(self.class_table, classes)
        self.fill_table(self.booking_table, bookings)
        self.customer_box["values"] = [f"{row[0]} - {row[1]}" for row in customers]

    def add_customer(self):
        name = self.customer_name.get().strip()
        email = self.customer_email.get().strip()
        phone = self.customer_phone.get().strip()
        if not name or "@" not in email:
            messagebox.showerror("Błąd", "Podaj imię, nazwisko i poprawny e-mail.")
            return
        try:
            db = connect_db()
            db.execute("INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)", (name, email, phone))
            db.commit()
            db.close()
            self.customer_name.set("")
            self.customer_email.set("")
            self.customer_phone.set("")
            self.refresh_all()
        except sqlite3.IntegrityError:
            messagebox.showerror("Błąd", "Klient z takim e-mailem już istnieje.")

    def select_customer(self, event):
        selected = self.customer_table.selection()
        if selected:
            row = self.customer_table.item(selected[0], "values")
            self.customer_name.set(row[1])
            self.customer_email.set(row[2])
            self.customer_phone.set(row[3] or "")

    def edit_customer(self):
        selected = self.customer_table.selection()
        if not selected:
            messagebox.showerror("Błąd", "Wybierz klienta z listy.")
            return
        row = self.customer_table.item(selected[0], "values")
        name = self.customer_name.get().strip()
        email = self.customer_email.get().strip()
        phone = self.customer_phone.get().strip()
        if not name or "@" not in email:
            messagebox.showerror("Błąd", "Podaj imię, nazwisko i poprawny e-mail.")
            return
        try:
            db = connect_db()
            db.execute("UPDATE customers SET name = ?, email = ?, phone = ? WHERE id = ?", (name, email, phone, row[0]))
            db.commit()
            db.close()
            self.refresh_all()
        except sqlite3.IntegrityError:
            messagebox.showerror("Błąd", "Ten e-mail jest już używany.")

    def delete_customer(self):
        selected = self.customer_table.selection()
        if not selected:
            messagebox.showerror("Błąd", "Wybierz klienta z listy.")
            return
        row = self.customer_table.item(selected[0], "values")
        if messagebox.askyesno("Potwierdzenie", "Usunąć wybranego klienta i jego zapisy?"):
            db = connect_db()
            db.execute("DELETE FROM customers WHERE id = ?", (row[0],))
            db.commit()
            db.close()
            self.refresh_all()

    def add_membership(self):
        customer = self.membership_customer.get().split(" - ")[0]
        start = self.membership_start.get().strip()
        end = self.membership_end.get().strip()
        try:
            date.fromisoformat(start)
            date.fromisoformat(end)
            if not customer or end < start:
                raise ValueError
            db = connect_db()
            db.execute("INSERT INTO memberships (customer_id, plan, start_date, end_date) VALUES (?, ?, ?, ?)", (int(customer), self.membership_plan.get(), start, end))
            db.commit()
            db.close()
            self.refresh_all()
        except (ValueError, sqlite3.IntegrityError):
            messagebox.showerror("Błąd", "Sprawdź klienta i daty karnetu.")

    def add_trainer(self):
        name = self.trainer_name.get().strip()
        specialty = self.trainer_specialty.get().strip()
        if not name:
            messagebox.showerror("Błąd", "Podaj imię i nazwisko trenera.")
            return
        db = connect_db()
        db.execute("INSERT INTO trainers (name, specialty) VALUES (?, ?)", (name, specialty))
        db.commit()
        db.close()
        self.trainer_name.set("")
        self.trainer_specialty.set("")
        self.refresh_all()

    def add_class(self):
        try:
            name = self.class_name.get().strip()
            trainer = self.class_trainer.get().strip()
            class_date = self.class_date.get().strip()
            class_time = self.class_time.get().strip()
            capacity = int(self.class_capacity.get())
            date.fromisoformat(class_date)
            trainer_id = int(trainer) if trainer else None
            if not name or capacity < 1:
                raise ValueError
            db = connect_db()
            db.execute("INSERT INTO classes (name, trainer_id, class_date, class_time, capacity) VALUES (?, ?, ?, ?, ?)", (name, trainer_id, class_date, class_time, capacity))
            db.commit()
            db.close()
            self.refresh_all()
        except (ValueError, sqlite3.IntegrityError):
            messagebox.showerror("Błąd", "Sprawdź nazwę, ID trenera, datę i limit miejsc.")

    def add_booking(self):
        try:
            customer_id = int(self.booking_customer.get())
            class_id = int(self.booking_class.get())
            db = connect_db()
            class_row = db.execute("SELECT capacity FROM classes WHERE id = ?", (class_id,)).fetchone()
            count = db.execute("SELECT COUNT(*) FROM bookings WHERE class_id = ?", (class_id,)).fetchone()[0]
            if class_row is None or count >= class_row[0]:
                db.close()
                messagebox.showerror("Błąd", "Nie ma zajęć lub brakuje miejsc.")
                return
            db.execute("INSERT INTO bookings (customer_id, class_id) VALUES (?, ?)", (customer_id, class_id))
            db.commit()
            db.close()
            self.refresh_all()
        except (ValueError, sqlite3.IntegrityError):
            messagebox.showerror("Błąd", "Sprawdź ID klienta, ID zajęć i czy klient nie jest już zapisany.")


def main():
    create_tables()
    root = tk.Tk()
    GymManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()

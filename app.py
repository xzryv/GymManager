import sqlite3
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox
from datetime import date
from customer_memberships import get_customers, add_customer, edit_customer, delete_customer, get_memberships, add_membership

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

    def make_styled_table(self, parent, columns, labels, widths):
        frame = tk.Frame(parent, background="white", highlightbackground="#dce3ed", highlightthickness=1)
        frame.pack(fill="both", expand=True)
        table = ttk.Treeview(frame, columns=columns, show="headings", height=7, style="Schedule.Treeview")
        for column, label, width in zip(columns, labels, widths):
            table.heading(column, text=label)
            table.column(column, width=width, minwidth=width, anchor="w" if column not in ("id", "status") else "center", stretch=column not in ("id", "status"))
        table.tag_configure("alternate", background="#f1f5f9")
        table.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        table.configure(yscrollcommand=scrollbar.set)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        return table

    def make_customers(self):
        tab = tk.Frame(self.tabs, background="#f1f5f9", padx=22, pady=18)
        self.tabs.add(tab, text="Klienci")
        header = tk.Frame(tab, background="#f1f5f9")
        header.pack(fill="x", pady=(0, 16))
        tk.Label(header, text="Klienci siłowni", font=("Segoe UI", 22, "bold"), foreground="#172b4d", background="#f1f5f9").pack(anchor="w")
        tk.Label(header, text="Dodawaj klientów i zarządzaj ich danymi.", font=("Segoe UI", 10), foreground="#64748b", background="#f1f5f9").pack(anchor="w", pady=(3, 0))
        card = tk.Frame(tab, background="white", padx=18, pady=14, highlightbackground="#dce3ed", highlightthickness=1)
        card.pack(fill="x")
        tk.Label(card, text="Dane klienta", font=("Segoe UI", 12, "bold"), foreground="#172b4d", background="white").pack(anchor="w", pady=(0, 10))
        form = tk.Frame(card, background="white")
        form.pack(fill="x")
        self.customer_name = tk.StringVar()
        self.customer_email = tk.StringVar()
        self.customer_phone = tk.StringVar()
        fields = [("Imię i nazwisko", self.customer_name), ("E-mail", self.customer_email), ("Telefon", self.customer_phone)]
        for column, (label, value) in enumerate(fields):
            tk.Label(form, text=label, font=("Segoe UI", 10), foreground="#475569", background="white").grid(row=0, column=column, sticky="w", padx=(0, 12), pady=(0, 5))
            ttk.Entry(form, textvariable=value, style="Schedule.TEntry").grid(row=1, column=column, sticky="ew", padx=(0, 12), pady=(0, 10))
            form.columnconfigure(column, weight=1, uniform="customer")
        actions = tk.Frame(card, background="white")
        actions.pack(fill="x", pady=(2, 0))
        tk.Button(actions, text="+  Dodaj klienta", command=self.add_customer, font=("Segoe UI", 10, "bold"), background="#2563eb", foreground="white", activebackground="#1d4ed8", activeforeground="white", relief="flat", borderwidth=0, padx=15, pady=8, cursor="hand2").pack(side="left", padx=(0, 7))
        tk.Button(actions, text="Zapisz edycję", command=self.edit_customer, font=("Segoe UI", 10), background="#e2e8f0", foreground="#172b4d", activebackground="#cbd5e1", relief="flat", borderwidth=0, padx=13, pady=8, cursor="hand2").pack(side="left", padx=4)
        tk.Button(actions, text="Usuń klienta", command=self.delete_customer, font=("Segoe UI", 10), background="#fee2e2", foreground="#b91c1c", activebackground="#fecaca", relief="flat", borderwidth=0, padx=13, pady=8, cursor="hand2").pack(side="left", padx=4)
        self.customer_notice = tk.StringVar()
        tk.Label(actions, textvariable=self.customer_notice, font=("Segoe UI", 10), foreground="#15803d", background="white").pack(side="left", padx=12)
        list_header = tk.Frame(tab, background="#f1f5f9")
        list_header.pack(fill="x", pady=(18, 8))
        tk.Label(list_header, text="Lista klientów", font=("Segoe UI", 12, "bold"), foreground="#172b4d", background="#f1f5f9").pack(side="left")
        self.customer_count = tk.StringVar(value="Liczba klientów: 0")
        tk.Label(list_header, textvariable=self.customer_count, font=("Segoe UI", 10), foreground="#64748b", background="#f1f5f9").pack(side="left", padx=12)
        ttk.Button(list_header, text="Odśwież", command=self.refresh_all, style="Schedule.TButton").pack(side="right")
        self.customer_table = self.make_styled_table(tab, ("id", "name", "email", "phone"), ("ID", "Imię i nazwisko", "E-mail", "Telefon"), (55, 230, 250, 150))
        self.customer_table.bind("<<TreeviewSelect>>", self.select_customer)
        tk.Label(tab, text="Wybierz klienta z tabeli, aby wczytać jego dane do edycji.", font=("Segoe UI", 9), foreground="#64748b", background="#f1f5f9").pack(anchor="w", pady=(8, 0))


    def make_memberships(self):
        tab = tk.Frame(self.tabs, background="#f1f5f9", padx=22, pady=18)
        self.tabs.add(tab, text="Karnety")
        header = tk.Frame(tab, background="#f1f5f9")
        header.pack(fill="x", pady=(0, 16))
        tk.Label(header, text="Karnety klientów", font=("Segoe UI", 22, "bold"), foreground="#172b4d", background="#f1f5f9").pack(anchor="w")
        tk.Label(header, text="Przypisuj karnety i sprawdzaj ich ważność.", font=("Segoe UI", 10), foreground="#64748b", background="#f1f5f9").pack(anchor="w", pady=(3, 0))
        card = tk.Frame(tab, background="white", padx=18, pady=14, highlightbackground="#dce3ed", highlightthickness=1)
        card.pack(fill="x")
        tk.Label(card, text="Nowy karnet", font=("Segoe UI", 12, "bold"), foreground="#172b4d", background="white").pack(anchor="w", pady=(0, 10))
        form = tk.Frame(card, background="white")
        form.pack(fill="x")
        self.membership_customer = tk.StringVar()
        self.membership_plan = tk.StringVar(value="1 miesiąc")
        self.membership_start = tk.StringVar()
        self.membership_end = tk.StringVar()
        fields = [("Klient", self.membership_customer), ("Rodzaj karnetu", self.membership_plan), ("Data rozpoczęcia · RRRR-MM-DD", self.membership_start), ("Data zakończenia · RRRR-MM-DD", self.membership_end)]
        for column, (label, value) in enumerate(fields):
            tk.Label(form, text=label, font=("Segoe UI", 10), foreground="#475569", background="white").grid(row=0, column=column, sticky="w", padx=(0, 12), pady=(0, 5))
            if value is self.membership_customer:
                widget = ttk.Combobox(form, textvariable=value, state="readonly", style="Schedule.TCombobox")
                self.customer_box = widget
            elif value is self.membership_plan:
                widget = ttk.Combobox(form, textvariable=value, values=("1 miesiąc", "3 miesiące", "12 miesięcy", "Jednorazowy"), state="readonly", style="Schedule.TCombobox")
            else:
                widget = ttk.Entry(form, textvariable=value, style="Schedule.TEntry")
            widget.grid(row=1, column=column, sticky="ew", padx=(0, 12), pady=(0, 10))
            form.columnconfigure(column, weight=1, uniform="membership")
        actions = tk.Frame(card, background="white")
        actions.pack(fill="x", pady=(2, 0))
        tk.Button(actions, text="+  Dodaj karnet", command=self.add_membership, font=("Segoe UI", 10, "bold"), background="#2563eb", foreground="white", activebackground="#1d4ed8", activeforeground="white", relief="flat", borderwidth=0, padx=15, pady=8, cursor="hand2").pack(side="left")
        self.membership_notice = tk.StringVar()
        tk.Label(actions, textvariable=self.membership_notice, font=("Segoe UI", 10), foreground="#15803d", background="white").pack(side="left", padx=12)
        list_header = tk.Frame(tab, background="#f1f5f9")
        list_header.pack(fill="x", pady=(18, 8))
        tk.Label(list_header, text="Lista karnetów", font=("Segoe UI", 12, "bold"), foreground="#172b4d", background="#f1f5f9").pack(side="left")
        self.membership_count = tk.StringVar(value="Liczba karnetów: 0")
        tk.Label(list_header, textvariable=self.membership_count, font=("Segoe UI", 10), foreground="#64748b", background="#f1f5f9").pack(side="left", padx=12)
        ttk.Button(list_header, text="Odśwież", command=self.refresh_all, style="Schedule.TButton").pack(side="right")
        self.membership_table = self.make_styled_table(tab, ("id", "customer", "plan", "start", "end", "status"), ("ID", "Klient", "Rodzaj", "Od", "Do", "Status"), (45, 190, 125, 105, 105, 115))
        self.membership_table.tag_configure("Aktywny", foreground="#15803d", background="#f0fdf4")
        self.membership_table.tag_configure("Wygasły", foreground="#b91c1c", background="#fef2f2")
        self.membership_table.tag_configure("Zaplanowany", foreground="#1d4ed8", background="#eff6ff")
        tk.Label(tab, text="Status jest ustalany automatycznie na podstawie dat karnetu.", font=("Segoe UI", 9), foreground="#64748b", background="#f1f5f9").pack(anchor="w", pady=(8, 0))

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
        customers = get_customers()
        trainers = db.execute("SELECT id, name, specialty FROM trainers ORDER BY name").fetchall()
        memberships = get_memberships()
        classes = db.execute("SELECT classes.id, classes.name, COALESCE(trainers.name, ''), classes.class_date, classes.class_time, classes.capacity, COUNT(bookings.id) FROM classes LEFT JOIN trainers ON trainers.id = classes.trainer_id LEFT JOIN bookings ON bookings.class_id = classes.id GROUP BY classes.id ORDER BY classes.class_date, classes.class_time").fetchall()
        bookings = db.execute("SELECT bookings.id, customers.name, classes.name, classes.class_date, classes.class_time FROM bookings JOIN customers ON customers.id = bookings.customer_id JOIN classes ON classes.id = bookings.class_id ORDER BY classes.class_date, classes.class_time").fetchall()
        db.close()
        self.fill_table(self.customer_table, customers)
        for index, item in enumerate(self.customer_table.get_children()):
            self.customer_table.item(item, tags=("alternate",) if index % 2 else ())
        self.customer_count.set(f"Liczba klientów: {len(customers)}")
        self.fill_table(self.trainer_table, trainers)
        self.fill_table(self.membership_table, memberships)
        for item in self.membership_table.get_children():
            values = self.membership_table.item(item, "values")
            self.membership_table.item(item, tags=(values[5],))
        self.membership_count.set(f"Liczba karnetów: {len(memberships)}")
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
            add_customer(name, email, phone)
            self.customer_name.set("")
            self.customer_email.set("")
            self.customer_phone.set("")
            self.refresh_all()
            self.customer_notice.set("Klient został dodany.")
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
            edit_customer(row[0], name, email, phone)
            self.refresh_all()
            self.customer_notice.set("Dane klienta zostały zapisane.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Błąd", "Ten e-mail jest już używany.")

    def delete_customer(self):
        selected = self.customer_table.selection()
        if not selected:
            messagebox.showerror("Błąd", "Wybierz klienta z listy.")
            return
        row = self.customer_table.item(selected[0], "values")
        if messagebox.askyesno("Potwierdzenie", "Usunąć wybranego klienta i jego zapisy?"):
            delete_customer(row[0])
            self.refresh_all()
            self.customer_notice.set("Klient został usunięty.")

    def add_membership(self):
        customer = self.membership_customer.get().split(" - ")[0]
        start = self.membership_start.get().strip()
        end = self.membership_end.get().strip()
        try:
            add_membership(int(customer), self.membership_plan.get(), start, end)
            self.membership_start.set("")
            self.membership_end.set("")
            self.refresh_all()
            self.membership_notice.set("Karnet został dodany.")
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



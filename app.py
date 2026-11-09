import hashlib
import hmac
import secrets
import sqlite3
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox
from datetime import date, time
from customer_memberships import get_customers, add_customer, edit_customer, delete_customer, get_memberships, add_membership

DB = Path(__file__).with_name("gymmanager.db")


def connect_db():
    db = sqlite3.connect(DB)
    db.execute("PRAGMA foreign_keys = ON")
    return db


def create_tables():
    db = connect_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT NOT NULL UNIQUE,
        password_salt BLOB NOT NULL,
        password_hash BLOB NOT NULL
    );
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


def has_users():
    db = connect_db()
    try:
        return db.execute("SELECT 1 FROM users LIMIT 1").fetchone() is not None
    finally:
        db.close()


def create_first_account(login, password):
    create_account(login, password, first_only=True)


def create_account(login, password, first_only=False):
    login = login.strip()
    if not login or not password.strip():
        raise ValueError("Podaj login i hasło.")
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 600000)
    db = connect_db()
    try:
        db.execute("BEGIN IMMEDIATE")
        if first_only and db.execute("SELECT 1 FROM users LIMIT 1").fetchone():
            raise ValueError("Pierwsze konto już istnieje. Zaloguj się.")
        db.execute("INSERT INTO users (login, password_salt, password_hash) VALUES (?, ?, ?)", (login, salt, password_hash))
        db.commit()
    except sqlite3.IntegrityError:
        raise ValueError("Ten login jest już zajęty. Wybierz inny.") from None
    finally:
        db.close()


def authenticate(login, password):
    if not login.strip() or not password.strip():
        return False
    db = connect_db()
    try:
        user = db.execute("SELECT password_salt, password_hash FROM users WHERE login = ?", (login.strip(),)).fetchone()
    finally:
        db.close()
    if user is None:
        return False
    password_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), user[0], 600000)
    return hmac.compare_digest(password_hash, user[1])


class GymManager:
    def __init__(self, root, on_logout):
        self.root = root
        self.root.title("GymManager - system siłowni")
        self.root.geometry("920x620")
        self.root.minsize(860, 620)
        ttk.Button(root, text="Wyloguj", command=on_logout).pack(anchor="e", padx=10, pady=(10, 0))
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
        style = ttk.Style(self.root)
        style.configure("Schedule.Treeview", font=("Segoe UI", 10), rowheight=34, background="#ffffff", fieldbackground="#ffffff", foreground="#243247")
        style.configure("Schedule.Treeview.Heading", font=("Segoe UI", 10, "bold"), padding=(8, 10))
        style.map("Schedule.Treeview", background=[("selected", "#dbeafe")], foreground=[("selected", "#153e75")])
        style.configure("Schedule.TEntry", padding=6)
        style.configure("Schedule.TCombobox", padding=6)
        style.configure("Schedule.TButton", font=("Segoe UI", 10), padding=(12, 7))
        tab = tk.Frame(self.tabs, background="#f1f5f9", padx=22, pady=18)
        self.tabs.add(tab, text="Zajęcia")
        header = tk.Frame(tab, background="#f1f5f9")
        header.pack(fill="x", pady=(0, 16))
        tk.Label(header, text="Harmonogram zajęć", font=("Segoe UI", 22, "bold"), foreground="#172b4d", background="#f1f5f9").pack(anchor="w")
        tk.Label(header, text="Zaplanuj treningi i sprawdź nadchodzące terminy.", font=("Segoe UI", 10), foreground="#64748b", background="#f1f5f9").pack(anchor="w", pady=(3, 0))
        card = tk.Frame(tab, background="white", padx=18, pady=14, highlightbackground="#dce3ed", highlightthickness=1)
        card.pack(fill="x")
        tk.Label(card, text="Nowe zajęcia", font=("Segoe UI", 12, "bold"), foreground="#172b4d", background="white").pack(anchor="w", pady=(0, 10))
        form = tk.Frame(card, background="white")
        form.pack(fill="x")
        self.class_name = tk.StringVar()
        self.class_trainer = tk.StringVar()
        self.class_date = tk.StringVar()
        self.class_time = tk.StringVar()
        self.class_capacity = tk.StringVar(value="10")
        fields = [("Nazwa zajęć", self.class_name, 0, 0, 3), ("Trener", self.class_trainer, 0, 3, 3), ("Data · RRRR-MM-DD", self.class_date, 2, 0, 2), ("Godzina · GG:MM", self.class_time, 2, 2, 2), ("Limit miejsc", self.class_capacity, 2, 4, 2)]
        for label, value, row, column, span in fields:
            tk.Label(form, text=label, font=("Segoe UI", 10), foreground="#475569", background="white").grid(row=row, column=column, columnspan=span, sticky="w", padx=(0, 12), pady=(0, 5))
            if value is self.class_trainer:
                widget = ttk.Combobox(form, textvariable=value, state="readonly", style="Schedule.TCombobox", width=18)
                self.class_trainer_box = widget
            else:
                widget = ttk.Entry(form, textvariable=value, style="Schedule.TEntry", width=12)
            widget.grid(row=row + 1, column=column, columnspan=span, sticky="ew", padx=(0, 12), pady=(0, 10))
        for column in range(6):
            form.columnconfigure(column, weight=1, uniform="schedule")
        actions = tk.Frame(card, background="white")
        actions.pack(fill="x", pady=(2, 0))
        tk.Button(actions, text="+  Dodaj zajęcia", command=self.add_class, font=("Segoe UI", 10, "bold"), background="#2563eb", foreground="white", activebackground="#1d4ed8", activeforeground="white", relief="flat", borderwidth=0, padx=18, pady=9, cursor="hand2").pack(side="left")
        self.class_notice = tk.StringVar()
        tk.Label(actions, textvariable=self.class_notice, font=("Segoe UI", 10), foreground="#15803d", background="white", wraplength=440, justify="left").pack(side="left", padx=14)
        list_header = tk.Frame(tab, background="#f1f5f9")
        list_header.pack(fill="x", pady=(18, 8))
        tk.Label(list_header, text="Zaplanowane zajęcia", font=("Segoe UI", 12, "bold"), foreground="#172b4d", background="#f1f5f9").pack(side="left")
        self.class_count = tk.StringVar()
        tk.Label(list_header, textvariable=self.class_count, font=("Segoe UI", 10), foreground="#64748b", background="#f1f5f9").pack(side="left", padx=12)
        ttk.Button(list_header, text="Odśwież", command=self.refresh_all, style="Schedule.TButton").pack(side="right")
        table_frame = tk.Frame(tab, background="white")
        table_frame.pack(fill="both", expand=True)
        columns = ("id", "name", "trainer", "date", "time", "capacity", "booked")
        self.class_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=5, style="Schedule.Treeview")
        for column, label, width in zip(columns, ("ID", "Zajęcia", "Trener", "Data", "Godzina", "Limit", "Zapisy"), (42, 180, 160, 110, 80, 65, 65)):
            self.class_table.heading(column, text=label)
            self.class_table.column(column, width=width, minwidth=width, stretch=column in ("name", "trainer"), anchor="w" if column in ("name", "trainer") else "center")
        self.class_table.tag_configure("alternate", background="#f1f5f9")
        self.class_table.grid(row=0, column=0, sticky="nsew")
        vertical_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.class_table.yview)
        vertical_scroll.grid(row=0, column=1, sticky="ns")
        horizontal_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.class_table.xview)
        horizontal_scroll.grid(row=1, column=0, sticky="ew")
        self.class_table.configure(yscrollcommand=vertical_scroll.set, xscrollcommand=horizontal_scroll.set)
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.class_empty = tk.Label(table_frame, text="Brak zaplanowanych zajęć.\nDodaj pierwsze zajęcia, korzystając z formularza powyżej.", font=("Segoe UI", 11), foreground="#64748b", background="white", justify="center")
        tk.Label(tab, text="Terminy uporządkowane według daty i godziny  •  Wszystkie pola formularza są wymagane", font=("Segoe UI", 9), foreground="#64748b", background="#f1f5f9").pack(anchor="w", pady=(8, 0))

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
        for index, item in enumerate(self.class_table.get_children()):
            self.class_table.item(item, tags=("alternate",) if index % 2 else ())
        self.class_count.set(f"Liczba zajęć: {len(classes)}")
        if classes:
            self.class_empty.place_forget()
        else:
            self.class_empty.place(relx=0.5, rely=0.55, anchor="center")
        self.fill_table(self.booking_table, bookings)
        self.class_trainers = {f"{row[0]} - {row[1]}": row[0] for row in trainers}
        self.class_trainer_box["values"] = list(self.class_trainers)
        if self.class_trainer.get() not in self.class_trainers:
            self.class_trainer.set("")
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
        self.class_notice.set("")
        db = None
        try:
            name = self.class_name.get().strip()
            class_date = self.class_date.get().strip()
            class_time = self.class_time.get().strip()
            if not name:
                raise ValueError("Podaj nazwę zajęć.")
            try:
                parsed_date = date.fromisoformat(class_date)
                if parsed_date.isoformat() != class_date:
                    raise ValueError
            except ValueError:
                raise ValueError("Podaj poprawną datę w formacie RRRR-MM-DD.")
            try:
                parsed_time = time.fromisoformat(class_time)
                if parsed_time.strftime("%H:%M") != class_time:
                    raise ValueError
            except ValueError:
                raise ValueError("Podaj poprawną godzinę w formacie GG:MM (00:00–23:59).")
            try:
                capacity = int(self.class_capacity.get())
                if capacity < 1:
                    raise ValueError
            except ValueError:
                raise ValueError("Limit miejsc musi być liczbą całkowitą większą od zera.")
            trainer_id = self.class_trainers.get(self.class_trainer.get())
            db = connect_db()
            if trainer_id is None or db.execute("SELECT id FROM trainers WHERE id = ?", (trainer_id,)).fetchone() is None:
                raise ValueError("Wybierz istniejącego trenera z listy.")
            db.execute("INSERT INTO classes (name, trainer_id, class_date, class_time, capacity) VALUES (?, ?, ?, ?, ?)", (name, trainer_id, class_date, class_time, capacity))
            db.commit()
        except ValueError as error:
            messagebox.showerror("Błąd", str(error))
            return
        except sqlite3.Error:
            messagebox.showerror("Błąd", "Nie udało się zapisać zajęć. Sprawdź dostęp do bazy i wybranego trenera.")
            return
        finally:
            if db is not None:
                db.close()
        self.class_name.set("")
        self.class_date.set("")
        self.class_time.set("")
        self.class_capacity.set("10")
        self.refresh_all()
        self.class_notice.set("Zajęcia zostały dodane do harmonogramu.")

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


class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.show_login()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login(self, register=None):
        self.clear_window()
        self.first_account = not has_users()
        self.registering = self.first_account if register is None else register
        self.root.title("GymManager - logowanie")
        self.root.geometry("920x700")
        self.root.minsize(860, 700)
        page = tk.Frame(self.root, background="#f1f5f9")
        page.pack(fill="both", expand=True)
        sidebar = tk.Frame(page, background="#14243b", width=300, padx=32, pady=36)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        logo = tk.Canvas(sidebar, width=48, height=48, background="#2563eb", highlightthickness=0)
        logo.pack(anchor="w", pady=(0, 18))
        logo.create_line(13, 24, 35, 24, fill="white", width=4)
        for x, top, bottom in ((12, 17, 31), (17, 13, 35), (31, 13, 35), (36, 17, 31)):
            logo.create_line(x, top, x, bottom, fill="white", width=4)
        tk.Label(sidebar, text="GymManager", font=("Segoe UI", 24, "bold"), background="#14243b", foreground="white").pack(anchor="w")
        tk.Label(sidebar, text="Twoja siłownia. Jeden system.", font=("Segoe UI", 10), background="#14243b", foreground="#a8b9ce").pack(anchor="w", pady=(8, 40))
        tk.Frame(sidebar, background="#365171", height=2, width=40).pack(anchor="w", pady=(0, 24))
        tk.Label(sidebar, text="Więcej czasu\nna dobry trening.", font=("Segoe UI", 21, "bold"), justify="left", background="#14243b", foreground="white").pack(anchor="w")
        tk.Label(sidebar, text="Klienci, karnety i zajęcia\nzawsze pod ręką.", font=("Segoe UI", 11), justify="left", background="#14243b", foreground="#a8b9ce").pack(anchor="w", pady=(14, 0))
        tk.Label(sidebar, text="SYSTEM ZARZĄDZANIA SIŁOWNIĄ", font=("Segoe UI", 8, "bold"), background="#14243b", foreground="#a8b9ce").pack(side="bottom", anchor="w")
        content = tk.Frame(page, background="#f1f5f9", padx=36, pady=20)
        content.pack(side="left", fill="both", expand=True)
        card = tk.Frame(content, background="white", highlightbackground="#dce3ed", highlightthickness=1, padx=30, pady=22)
        card.pack(fill="x", expand=True)
        choices = tk.Frame(card, background="white")
        choices.pack(fill="x", pady=(0, 20))
        for column, (text, register) in enumerate((("Zaloguj się", False), ("Zarejestruj się", True))):
            selected = self.registering == register
            tk.Button(choices, text=text, command=lambda mode=register: self.show_login(mode), font=("Segoe UI", 10, "bold"), background="#2563eb" if selected else "#eff6ff", foreground="white" if selected else "#2563eb", activebackground="#1d4ed8", activeforeground="white", relief="flat", borderwidth=0, pady=10, cursor="hand2").grid(row=0, column=column, sticky="ew", padx=(0, 4) if column == 0 else (4, 0))
            choices.columnconfigure(column, weight=1, uniform="login_choices")
        badge = "REJESTRACJA KONTA" if self.registering else "PANEL PRACOWNIKA"
        tk.Label(card, text=badge, font=("Segoe UI", 9, "bold"), foreground="#2563eb", background="white").pack(anchor="w", pady=(0, 12))
        title = ("Utwórz pierwsze konto" if self.first_account else "Utwórz konto") if self.registering else "Witaj ponownie"
        tk.Label(card, text=title, font=("Segoe UI", 23, "bold"), foreground="#172b4d", background="white").pack(anchor="w")
        subtitle = "Ustal dane, których użyjesz do logowania." if self.registering else "Zaloguj się, aby zarządzać swoją siłownią."
        tk.Label(card, text=subtitle, font=("Segoe UI", 10), foreground="#64748b", background="white", wraplength=370, justify="left").pack(anchor="w", pady=(6, 16))
        self.login = tk.StringVar(master=self.root)
        self.password = tk.StringVar(master=self.root)
        self.notice = tk.StringVar(master=self.root)
        login_entry = self.make_login_field(card, "Login", self.login)
        self.password_entry = self.make_login_field(card, "Hasło", self.password, show="*")
        self.show_password = tk.BooleanVar(master=self.root, value=False)
        tk.Checkbutton(card, text="Pokaż hasło", variable=self.show_password, command=self.toggle_password, font=("Segoe UI", 10), background="white", foreground="#475569", activebackground="white", activeforeground="#172b4d", selectcolor="white", cursor="hand2", padx=0, highlightthickness=0, borderwidth=0).pack(anchor="w", pady=(0, 16))
        action = "Utwórz konto" if self.registering else "Zaloguj się"
        button = tk.Button(card, text=action, command=self.submit, font=("Segoe UI", 11, "bold"), background="#2563eb", foreground="white", activebackground="#1d4ed8", activeforeground="white", relief="flat", borderwidth=0, pady=12, cursor="hand2", highlightthickness=2, highlightbackground="white", highlightcolor="#93c5fd")
        button.pack(fill="x")
        button.bind("<Enter>", lambda event: button.configure(background="#1d4ed8"))
        button.bind("<Leave>", lambda event: button.configure(background="#2563eb"))
        self.notice_label = tk.Label(card, textvariable=self.notice, foreground="#b91c1c", background="white", font=("Segoe UI", 10), wraplength=360, justify="left", anchor="w", height=2)
        self.notice_label.pack(fill="x", pady=(10, 0))
        tk.Button(content, text="Wejdź jako administrator (bez logowania)", command=self.open_admin, font=("Segoe UI", 10, "bold"), background="#e2e8f0", foreground="#334155", activebackground="#cbd5e1", activeforeground="#172b4d", relief="flat", borderwidth=0, pady=12, cursor="hand2").pack(fill="x", pady=(16, 0))
        login_entry.bind("<Return>", lambda event: self.submit())
        self.password_entry.bind("<Return>", lambda event: self.submit())
        login_entry.focus_set()

    def make_login_field(self, parent, label, value, show=""):
        tk.Label(parent, text=label, font=("Segoe UI", 10, "bold"), background="white", foreground="#334155").pack(anchor="w", pady=(0, 6))
        frame = tk.Frame(parent, background="white", highlightbackground="#cbd5e1", highlightcolor="#2563eb", highlightthickness=1)
        frame.pack(fill="x", pady=(0, 16))
        entry = tk.Entry(frame, textvariable=value, show=show, font=("Segoe UI", 12), background="white", foreground="#172b4d", insertbackground="#172b4d", relief="flat", borderwidth=0, width=20)
        entry.pack(fill="x", padx=12, pady=10)
        entry.bind("<FocusIn>", lambda event: frame.configure(highlightbackground="#2563eb"))
        entry.bind("<FocusOut>", lambda event: frame.configure(highlightbackground="#cbd5e1"))
        return entry

    def toggle_password(self):
        self.password_entry.configure(show="" if self.show_password.get() else "*")

    def open_main(self):
        self.password.set("")
        self.clear_window()
        GymManager(self.root, self.show_login)

    def open_admin(self):
        self.open_main()
        self.root.title("GymManager - administrator")

    def submit(self):
        self.notice_label.configure(foreground="#b91c1c")
        login = self.login.get().strip()
        password = self.password.get()
        if not login or not password.strip():
            self.notice.set("Podaj login i hasło.")
            return
        try:
            if self.registering:
                create_account(login, password)
                self.show_login(False)
                self.login.set(login)
                self.notice_label.configure(foreground="#15803d")
                self.notice.set("Konto utworzone. Zaloguj się.")
                return
            if not authenticate(login, password):
                self.password.set("")
                self.notice.set("Nieprawidłowy login lub hasło.")
                return
        except ValueError as error:
            self.notice.set(str(error))
            return
        except sqlite3.Error:
            self.notice.set("Nie udało się odczytać lub zapisać konta. Sprawdź dostęp do bazy.")
            return
        self.open_main()


def main():
    create_tables()
    root = tk.Tk()
    LoginScreen(root)
    root.mainloop()


if __name__ == "__main__":
    main()



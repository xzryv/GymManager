import sqlite3
from datetime import date
from pathlib import Path

DB = Path(__file__).with_name("gymmanager.db")


def connect_db():
    db = sqlite3.connect(DB)
    db.execute("PRAGMA foreign_keys = ON")
    return db


def get_customers():
    db = connect_db()
    rows = db.execute("SELECT id, name, email, phone FROM customers ORDER BY name").fetchall()
    db.close()
    return rows


def add_customer(name, email, phone):
    name = name.strip()
    email = email.strip()
    phone = phone.strip()
    if not name or "@" not in email:
        raise ValueError("Podaj imię, nazwisko i poprawny e-mail.")
    db = connect_db()
    db.execute("INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)", (name, email, phone))
    db.commit()
    db.close()


def edit_customer(customer_id, name, email, phone):
    name = name.strip()
    email = email.strip()
    phone = phone.strip()
    if not name or "@" not in email:
        raise ValueError("Podaj imię, nazwisko i poprawny e-mail.")
    db = connect_db()
    db.execute("UPDATE customers SET name = ?, email = ?, phone = ? WHERE id = ?", (name, email, phone, customer_id))
    db.commit()
    db.close()


def delete_customer(customer_id):
    db = connect_db()
    db.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
    db.commit()
    db.close()


def get_memberships():
    db = connect_db()
    rows = db.execute("SELECT memberships.id, customers.name, memberships.plan, memberships.start_date, memberships.end_date, CASE WHEN memberships.start_date > date('now') THEN 'Zaplanowany' WHEN memberships.end_date >= date('now') THEN 'Aktywny' ELSE 'Wygasły' END FROM memberships JOIN customers ON customers.id = memberships.customer_id ORDER BY memberships.end_date DESC").fetchall()
    db.close()
    return rows


def add_membership(customer_id, plan, start_date, end_date):
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError:
        raise ValueError("Wpisz poprawne daty w formacie RRRR-MM-DD.")
    if end < start:
        raise ValueError("Data końca nie może być wcześniejsza niż data początku.")
    db = connect_db()
    customer = db.execute("SELECT id FROM customers WHERE id = ?", (customer_id,)).fetchone()
    if customer is None:
        db.close()
        raise ValueError("Wybierz klienta.")
    db.execute("INSERT INTO memberships (customer_id, plan, start_date, end_date) VALUES (?, ?, ?, ?)", (customer_id, plan, start.isoformat(), end.isoformat()))
    db.commit()
    db.close()

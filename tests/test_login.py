import sqlite3
import subprocess
import sys
import tempfile
import tkinter as tk
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app
import customer_memberships


class LoginTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.original_db = app.DB
        self.original_customers_db = customer_memberships.DB
        app.DB = Path(self.directory.name) / "gymmanager.db"
        customer_memberships.DB = app.DB
        app.create_tables()
        self.root = tk.Tk()
        self.root.withdraw()
        self.screen = app.LoginScreen(self.root)

    def tearDown(self):
        self.root.destroy()
        app.DB = self.original_db
        customer_memberships.DB = self.original_customers_db
        self.directory.cleanup()

    def submit(self, login, password):
        self.screen.login.set(login)
        self.screen.password.set(password)
        self.screen.submit()

    def create_account(self):
        self.submit("pracownik", "Zażółć-123!")

    def assert_login_visible(self):
        self.assertEqual(self.root.title(), "GymManager - logowanie")
        self.assertFalse(any(isinstance(widget, app.ttk.Notebook) for widget in self.root.winfo_children()))

    def test_first_launch_requires_account_and_login(self):
        self.assertTrue(self.screen.first_account)
        self.assert_login_visible()
        self.create_account()
        self.assertFalse(self.screen.first_account)
        self.assertIn("Konto utworzone", self.screen.notice.get())
        self.assert_login_visible()

    def test_empty_fields_are_rejected_in_setup_and_login(self):
        for setup in (True, False):
            if not setup:
                self.create_account()
            for login, password in (("", ""), ("", "hasło"), ("login", ""), ("   ", "hasło"), ("login", "   ")):
                self.submit(login, password)
                self.assertEqual(self.screen.notice.get(), "Podaj login i hasło.")
                self.assert_login_visible()
            self.assertEqual(app.has_users(), not setup)

    def test_invalid_credentials_do_not_open_main_window(self):
        self.create_account()
        for login, password in (("pracownik", "błędne"), ("nieznany", "Zażółć-123!"), ("' OR 1=1 --", "Zażółć-123!")):
            self.submit(login, password)
            self.assertEqual(self.screen.notice.get(), "Nieprawidłowy login lub hasło.")
            self.assertEqual(self.screen.password.get(), "")
            self.assert_login_visible()

    def test_login_logout_and_login_again(self):
        self.create_account()
        for attempt in range(2):
            self.submit("pracownik", "Zażółć-123!")
            notebooks = [widget for widget in self.root.winfo_children() if isinstance(widget, app.ttk.Notebook)]
            self.assertEqual(len(notebooks), 1)
            self.assertEqual(len(notebooks[0].tabs()), 5)
            logout = next(widget for widget in self.root.winfo_children() if isinstance(widget, app.ttk.Button) and widget.cget("text") == "Wyloguj")
            logout.invoke()
            self.assert_login_visible()
            self.assertEqual(self.screen.login.get(), "")
            self.assertEqual(self.screen.password.get(), "")
            self.assertFalse(self.screen.first_account)

    def test_password_is_hashed_and_persists_after_restart(self):
        self.create_account()
        with sqlite3.connect(app.DB) as db:
            login, salt, password_hash = db.execute("SELECT login, password_salt, password_hash FROM users").fetchone()
        self.assertEqual(login, "pracownik")
        self.assertEqual(len(salt), 16)
        self.assertEqual(len(password_hash), 32)
        self.assertNotIn("Zażółć-123!".encode("utf-8"), app.DB.read_bytes())
        code = "import app, sys; from pathlib import Path; app.DB = Path(sys.argv[1]); app.create_tables(); assert app.has_users(); assert app.authenticate('pracownik', 'Zażółć-123!'); assert not app.authenticate('pracownik', 'błędne')"
        subprocess.run([sys.executable, "-B", "-c", code, str(app.DB)], cwd=Path(app.__file__).parent, check=True)

    def test_first_account_cannot_be_replaced(self):
        self.create_account()
        with self.assertRaises(ValueError):
            app.create_first_account("inne", "nowe hasło")
        self.assertTrue(app.authenticate("pracownik", "Zażółć-123!"))
        self.assertFalse(app.authenticate("inne", "nowe hasło"))

    def test_account_setup_preserves_existing_data(self):
        with sqlite3.connect(app.DB) as db:
            db.execute("INSERT INTO customers (name, email) VALUES ('Klient', 'klient@example.com')")
        self.create_account()
        app.create_tables()
        with sqlite3.connect(app.DB) as db:
            self.assertEqual(db.execute("SELECT name, email FROM customers").fetchall(), [("Klient", "klient@example.com")])


if __name__ == "__main__":
    unittest.main()

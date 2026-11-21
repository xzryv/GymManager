import sys
import tempfile
import tkinter as tk
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
from threading import Barrier
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app
import customer_memberships


class BookingTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.original_db = app.DB
        self.original_customers_db = customer_memberships.DB
        app.DB = customer_memberships.DB = Path(self.directory.name) / 'test.db'
        app.create_tables()
        with closing(app.connect_db()) as db, db:
            db.executemany('INSERT INTO customers (name, email) VALUES (?, ?)', [('Anna', 'anna@example.com'), ('Jan', 'jan@example.com')])
            db.execute("INSERT INTO trainers (name) VALUES ('Trener')")
            db.executemany('INSERT INTO classes (name, trainer_id, class_date, class_time, capacity) VALUES (?, 1, ?, ?, ?)', [('Joga', '2099-01-01', '10:00', 1), ('Pilates', '2099-01-02', '12:00', 3), ('Archiwalne', '2000-01-01', '10:00', 5)])
        self.root = tk.Tk()
        self.root.withdraw()
        self.ui = app.GymManager(self.root, lambda: None)

    def tearDown(self):
        self.root.destroy()
        app.DB = self.original_db
        customer_memberships.DB = self.original_customers_db
        self.directory.cleanup()

    def select(self, customer_id, class_id):
        self.ui.booking_customer.set(next(label for label, value in self.ui.booking_customers.items() if value == customer_id))
        self.ui.booking_class.set(next(label for label, value in self.ui.booking_classes.items() if value == class_id))

    def count(self):
        with closing(app.connect_db()) as db:
            return db.execute('SELECT COUNT(*) FROM bookings').fetchone()[0]

    def test_save_filter_and_full_class_disappears(self):
        self.assertEqual(set(self.ui.booking_classes.values()), {1, 2})
        self.select(1, 1)
        self.ui.add_booking()
        self.assertEqual(self.count(), 1)
        self.assertNotIn(1, self.ui.booking_classes.values())
        rows = [self.ui.booking_table.item(item, 'values') for item in self.ui.booking_table.get_children()]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1:3], ('Anna', 'Joga'))
        self.ui.participant_class.set(next(label for label, value in self.ui.participant_classes.items() if value == 3))
        self.ui.refresh_participants()
        self.assertFalse(self.ui.booking_table.get_children())
        self.assertEqual(self.ui.participant_count.get(), 'Brak zapisanych uczestników.')

    def test_invalid_selections_are_rejected(self):
        with patch.object(app.messagebox, 'showerror') as error:
            self.ui.add_booking()
            self.assertIn('klienta', error.call_args.args[1])
            self.ui.booking_customer.set(next(iter(self.ui.booking_customers)))
            self.ui.add_booking()
            self.assertIn('zajęcia', error.call_args.args[1])
        self.assertEqual(self.count(), 0)

    def test_duplicate_full_past_and_missing_records(self):
        app.reserve_class(1, 1)
        for customer, training, text in [(1, 1, 'już zapisany'), (2, 1, 'Brak wolnych'), (1, 3, 'rozpoczęły'), (999, 2, 'klient nie istnieje'), (1, 999, 'zajęcia nie istnieją')]:
            with self.subTest(customer=customer, training=training):
                with self.assertRaisesRegex(ValueError, text):
                    app.reserve_class(customer, training)
        self.assertEqual(self.count(), 1)

    def test_stale_full_class_is_rejected_and_refreshed(self):
        self.select(2, 1)
        app.reserve_class(1, 1)
        with patch.object(app.messagebox, 'showerror') as error:
            self.ui.add_booking()
            self.assertIn('Brak wolnych', error.call_args.args[1])
        self.assertEqual(self.count(), 1)
        self.assertNotIn(1, self.ui.booking_classes.values())

    def test_concurrent_reservations_cannot_exceed_capacity(self):
        barrier = Barrier(2)
        def reserve(customer):
            barrier.wait()
            try:
                app.reserve_class(customer, 1)
                return True
            except ValueError:
                return False
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(reserve, (1, 2)))
        self.assertEqual(sorted(results), [False, True])
        self.assertEqual(self.count(), 1)

    def test_schedule_validation_still_works(self):
        self.ui.class_name.set('Trening')
        self.ui.class_trainer.set('1 - Trener')
        self.ui.class_date.set('2099-03-01')
        self.ui.class_time.set('09:00')
        self.ui.class_capacity.set('5')
        self.ui.add_class()
        self.assertEqual(len(self.ui.booking_classes), 3)
        self.ui.class_name.set('Błędne zajęcia')
        self.ui.class_date.set('2099-02-30')
        with patch.object(app.messagebox, 'showerror') as error:
            self.ui.add_class()
            error.assert_called_once()
        self.assertEqual(len(self.ui.booking_classes), 3)


if __name__ == '__main__':
    unittest.main()

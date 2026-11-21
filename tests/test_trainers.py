import sys
import tempfile
import tkinter as tk
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app
import customer_memberships


class TrainerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.original_db = app.DB
        self.original_customers_db = customer_memberships.DB
        app.DB = customer_memberships.DB = Path(self.directory.name) / 'test.db'
        app.create_tables()
        with closing(app.connect_db()) as db, db:
            db.execute("INSERT INTO trainers (name, specialty) VALUES ('Anna Nowak', 'Joga')")
            db.execute("INSERT INTO classes (name, class_date, class_time, capacity) VALUES ('Pilates', '2099-01-01', '12:00', 10)")
        self.root = tk.Tk()
        self.root.withdraw()
        self.ui = app.GymManager(self.root, lambda: None)

    def tearDown(self):
        self.root.destroy()
        app.DB = self.original_db
        customer_memberships.DB = self.original_customers_db
        self.directory.cleanup()

    def rows(self, query):
        with closing(app.connect_db()) as db:
            return db.execute(query).fetchall()

    def select(self):
        self.ui.trainer_table.selection_set(self.ui.trainer_table.get_children()[0])
        self.ui.select_trainer()

    def test_add_and_list_trainer(self):
        self.ui.trainer_name.set('  Jan Kowalski  ')
        self.ui.trainer_specialty.set('  Trening siłowy  ')
        self.ui.add_trainer()
        self.assertEqual(self.rows('SELECT name, specialty FROM trainers ORDER BY id')[1], ('Jan Kowalski', 'Trening siłowy'))
        self.assertEqual(len(self.ui.trainer_table.get_children()), 2)
        self.assertIn('2 - Jan Kowalski', self.ui.class_trainers)
        self.assertEqual(self.ui.trainer_name.get(), '')

    def test_empty_name_and_edit_without_selection_are_rejected(self):
        with patch.object(app.messagebox, 'showerror') as error:
            self.ui.trainer_name.set('   ')
            self.ui.add_trainer()
            self.assertIn('imię i nazwisko', error.call_args.args[1])
            self.ui.edit_trainer()
            self.assertIn('Wybierz trenera', error.call_args.args[1])
        self.assertEqual(len(self.rows('SELECT id FROM trainers')), 1)

    def test_edit_preserves_assignment_and_updates_schedule(self):
        self.select()
        self.ui.trainer_class.set(next(iter(self.ui.trainer_classes)))
        self.ui.assign_trainer()
        self.ui.trainer_name.set('Anna Wiśniewska')
        self.ui.trainer_specialty.set('')
        self.ui.edit_trainer()
        self.assertEqual(self.rows('SELECT name, specialty FROM trainers'), [('Anna Wiśniewska', '')])
        self.assertEqual(self.rows('SELECT trainer_id FROM classes'), [(1,)])
        row = self.ui.class_table.item(self.ui.class_table.get_children()[0], 'values')
        self.assertEqual(row[2], 'Anna Wiśniewska')
        self.assertIn('1 - Anna Wiśniewska', self.ui.class_trainers)

    def test_assign_requires_trainer_and_class(self):
        with patch.object(app.messagebox, 'showerror') as error:
            self.ui.assign_trainer()
            self.assertIn('Wybierz trenera', error.call_args.args[1])
            self.select()
            self.ui.assign_trainer()
            self.assertIn('Wybierz zajęcia', error.call_args.args[1])
        self.assertEqual(self.rows('SELECT trainer_id FROM classes'), [(None,)])

    def test_deleted_trainer_is_rejected_for_edit_and_assignment(self):
        self.select()
        self.ui.trainer_class.set(next(iter(self.ui.trainer_classes)))
        with closing(app.connect_db()) as db, db:
            db.execute('DELETE FROM trainers')
        with patch.object(app.messagebox, 'showerror') as error:
            self.ui.edit_trainer()
            self.assertIn('nie istnieje', error.call_args.args[1])
            self.ui.assign_trainer()
            self.assertIn('nie istnieje', error.call_args.args[1])
        self.assertEqual(self.rows('SELECT trainer_id FROM classes'), [(None,)])

    def test_deleted_class_is_rejected(self):
        self.select()
        self.ui.trainer_class.set(next(iter(self.ui.trainer_classes)))
        with closing(app.connect_db()) as db, db:
            db.execute('DELETE FROM classes')
        with patch.object(app.messagebox, 'showerror') as error:
            self.ui.assign_trainer()
            self.assertIn('zajęcia już nie istnieją', error.call_args.args[1])

    def test_database_error_is_reported(self):
        self.ui.trainer_name.set('Jan')
        with patch.object(app, 'connect_db', side_effect=app.sqlite3.OperationalError), patch.object(app.messagebox, 'showerror') as error:
            self.ui.add_trainer()
            self.assertIn('Nie udało się zapisać', error.call_args.args[1])

    def test_reassignment_preserves_class_details(self):
        with closing(app.connect_db()) as db, db:
            db.execute("INSERT INTO trainers (name) VALUES ('Jan Kowalski')")
        self.ui.refresh_all()
        self.select()
        self.ui.trainer_class.set(next(iter(self.ui.trainer_classes)))
        self.ui.assign_trainer()
        self.ui.trainer_table.selection_set(self.ui.trainer_table.get_children()[1])
        self.ui.select_trainer()
        self.ui.assign_trainer()
        self.assertEqual(self.rows('SELECT trainer_id, name, class_date, class_time, capacity FROM classes'), [(2, 'Pilates', '2099-01-01', '12:00', 10)])


if __name__ == '__main__':
    unittest.main()

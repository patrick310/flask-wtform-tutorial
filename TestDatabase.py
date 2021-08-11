import unittest
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date

class SimpleSqliteTest(unittest.TestCase):
    def setUp(self):
        print("Connecting DB")
        db_string = "sqlite://"

        self.db = create_engine(db_string)

    def tearDown(self):
        print("Disconnecting DB")
        del self.db

    def testCanCreateTableAndManageData(self):
        # Create
        self.db.execute("CREATE TABLE IF NOT EXISTS films (title text, director text, year text)")
        self.db.execute(
            "INSERT INTO films (title, director, year) VALUES ('Doctor Strange', 'Scott Derrickson', '2016')"
        )

        # Read
        result_set = self.db.execute("SELECT * FROM films")
        for r in result_set:
            self.assertEqual(int(r['year']), 2016, "Test value was not read read back correctly.")

        # Update
        self.db.execute("UPDATE films SET title='Some2016Film' WHERE year='2016'")

        # Delete
        self.db.execute("DELETE FROM films WHERE year='2016'")


class PostgresTest(unittest.TestCase):
    def setUp(self):
        print("Connecting DB")
        db_string = 'postgresql://uzbiy6sxtg1wi:smTY464FvRGfYMB@35.202.17.55/dbekqfrcjb4dfy'

        self.db = create_engine(db_string)

    def tearDown(self):
        print("Disconnecting DB")
        del self.db

    def testCanCreateTableAndManageData(self):
        # Create
        self.db.execute("CREATE TABLE IF NOT EXISTS films (title text, director text, year text)")
        self.db.execute(
            "INSERT INTO films (title, director, year) VALUES ('Doctor Strange', 'Scott Derrickson', '2016')"
        )

        # Read
        result_set = self.db.execute("SELECT * FROM films")
        for r in result_set:
            self.assertEqual(int(r['year']), 2016, "Test value was not read read back correctly.")

        # Update
        self.db.execute("UPDATE films SET title='Some2016Film' WHERE year='2016'")

        # Delete
        self.db.execute("DELETE FROM films WHERE year='2016'")


if __name__ == '__main__':
    unittest.main()

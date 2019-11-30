import sqlite3
import os


class DbAdapter:
    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()

    def create_table(self):
        pass

    def add(self, util_obj):
        pass

    def delete(self, util_obj):
        pass

    def get(self, util_type, _id=None):
        pass


PATH = "Salary.db"
db_adapter = DbAdapter(PATH)
if not os.path.isfile(PATH):
    db_adapter.create_table()

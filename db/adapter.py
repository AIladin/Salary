import sqlite3
import os
from db.db_types import Month, HArray, UtilTypes
import logging

DB_CREATION = ["""
CREATE TABLE professions(
            id integer PRIMARY KEY AUTOINCREMENT,
            name text,
            salary integer,
            min_hours integer);
""", """
CREATE TABLE workers(
            id integer PRIMARY KEY AUTOINCREMENT,
            name text,
            profession_id integer,
            FOREIGN KEY (profession_id) REFERENCES professions(id)
            );
""", """
CREATE TABLE blanks(
            id integer PRIMARY KEY AUTOINCREMENT,
            worker_id integer,
            data array,
            date month,
            FOREIGN KEY (worker_id) REFERENCES workers(id)
            );
"""]


class DbAdapter:

    def __init__(self, path):
        sqlite3.register_adapter(Month, Month.to_sqlite)
        sqlite3.register_converter("month", Month.from_sqlite)

        sqlite3.register_adapter(HArray, HArray.to_sqlite)
        sqlite3.register_converter("array", HArray.from_sqlite)

        self.conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
        self.cursor = self.conn.cursor()

    def create_table(self):
        logging.info("Creating table")
        for query in DB_CREATION:
            self.cursor.execute(query)
        self.conn.commit()
        logging.info("Table created")

    def add(self, util_obj):
        if util_obj.util_type == UtilTypes.PROFESSION:
            self._add_profession(util_obj)
        elif util_obj.util_type == UtilTypes.WORKER:
            self._add_worker(util_obj)
        elif util_obj.util_type == UtilTypes.BLANK:
            self._add_blank(util_obj)
        else:
            raise ValueError(f"Wrong util type {util_obj.util_type}.")

    def _add_profession(self, profession):
        if not profession.id:
            query = "INSERT INTO professions(name, salary, min_hours)" \
                    " VALUES (?, ?, ?)"
            params = (profession.name, profession.salary, profession.min_hours)

            logging.info("Adding profession")
        else:
            query = "UPDATE professions" \
                   " SET name=?, salary=?, min_hours=?" \
                   " WHERE id=?"
            params = (profession.name, profession.salary, profession.min_hours, profession.id)
            logging.info("Updating profession")

        self.cursor.execute(query, params)
        self.conn.commit()
        logging.info("Done")
        profession.id = self.cursor.lastrowid

    def _add_worker(self, worker):
        if not worker.id:
            query = "INSERT INTO workers(name, profession_id)" \
                    " VALUES (?, ?)"
            params = (worker.name, worker.profession.id)
            logging.info("Adding worker")
        else:
            query = "UPDATE workers" \
                   " SET name=?, profession_id=?" \
                   " WHERE id=?"
            params = (worker.name, worker.profession.id, worker.id)
            logging.info("Updating worker")
        self.cursor.execute(query, params)
        self.conn.commit()
        worker.id = self.cursor.lastrowid
        logging.info("Done")

    def _add_blank(self, blank):
        if not blank.id:
            query = "INSERT INTO blanks(data, date, worker_id)" \
                    " VALUES (?, ?, ?)"
            params = (blank.data, blank.month, blank.worker.id)
            logging.info("Adding blank")
        else:
            query = "UPDATE blanks" \
                   " SET data=?, date=?, worker_id=?" \
                   " WHERE id=?"
            params = (blank.data, blank.month, blank.worker.id, blank.id)
            logging.info("Updating blank")
        self.cursor.execute(query, params)
        self.conn.commit()
        logging.info("Done")
        blank.id = self.cursor.lastrowid

    def delete(self, util_obj):
        if util_obj.util_type == UtilTypes.PROFESSION:
            self.cursor.execute("DELETE FROM blanks "
                                " WHERE worker_id=("
                                "SELECT w.id FROM workers w WHERE"
                                " profession_id=?)", (util_obj.id, ))
            self.cursor.execute("DELETE FROM workers WHERE profession_id=?", (util_obj.id, ))
        if util_obj.util_type == UtilTypes.WORKER:
            self.cursor.execute("DELETE from blanks WHERE worker_id=?", (util_obj.id, ))
        logging.info(f"Deleting {util_obj.util_type}:{util_obj.id}")
        assert util_obj.id, "Object not in db"
        query = f"DELETE from {util_obj.util_type.value[0]} where id=?"
        self.cursor.execute(query, (util_obj.id,))
        self.conn.commit()
        logging.info("Done")

    def get(self, util_type, _id=None):
        logging.info(f"Getting {util_type}:{_id}")
        if util_type not in UtilTypes:
            raise ValueError(f"Wrong util type {util_type}")
        query = f"SELECT * FROM {util_type.value[0]} "
        if _id:
            query += "WHERE id=?"
            self.cursor.execute(query, (_id, ))
        else:
            self.cursor.execute(query)
        self.conn.commit()
        logging.info("Done")
        return self.cursor.fetchall()


PATH = "../db/Salary.db"
if not os.path.exists(PATH):
    db_adapter = DbAdapter(PATH)
    db_adapter.create_table()
else:
    db_adapter = DbAdapter(PATH)

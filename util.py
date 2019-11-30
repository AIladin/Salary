from datetime import date, timedelta
from db.adapter import db_adapter
from enum import Enum


class UtilTypes(Enum):
    PROFESSION = "Profession",
    WORKER = "Worker",
    BLANK = "Blank",


class UtilSuperclass:
    def __init__(self):
        self.util_type = None
        self.id = None

    @classmethod
    def from_db(cls, _id):
        return db_adapter.get(cls.util_type, _id=_id)

    def dump(self):
        db_adapter.add(self)


class Profession(UtilSuperclass):
    def __init__(self, name, salary, min_hours):
        super().__init__()
        self.util_type = UtilTypes.PROFESSION
        self.name = name
        self.salary = salary
        self.min_hours = min_hours


class Worker(UtilSuperclass):
    def __init__(self, name, profession):
        super().__init__()
        self.util_type = UtilTypes.WORKER
        self.name = name
        self.profession = profession


class Month(date):
    def __init__(self, month, year):
        super().__init__(year=year, month=month, day=28)

    def _last_day_of_month(self):
        next_month = self + timedelta(days=4)
        return next_month - timedelta(days=next_month.day)

    def __len__(self):
        return self._last_day_of_month().day


class Blank(UtilSuperclass):

    def __init__(self, data, month):
        super().__init__()
        self.util_type = UtilTypes.BLANK
        assert len(data) == len(month)
        self.data = data
        self.month = month

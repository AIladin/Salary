from db.db_types import UtilTypes
from db.adapter import db_adapter


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


class Blank(UtilSuperclass):

    def __init__(self, data, month, worker):
        super().__init__()
        self.util_type = UtilTypes.BLANK
        assert len(data) == len(month)
        self.data = data
        self.month = month
        self.worker = worker

from db.db_types import UtilTypes
from db.adapter import db_adapter


class UtilSuperclass:
    def __init__(self):
        if isinstance(self, Profession):
            self.util_type = UtilTypes.PROFESSION
        elif isinstance(self, Worker):
            self.util_type = UtilTypes.WORKER
        elif isinstance(self, Blank):
            self.util_type = UtilTypes.BLANK
        else:
            self.util_type = None
        self.id = None

    def __eq__(self, other):
        return self.id == other.id

    @classmethod
    def from_db(cls, _id=None):
        rez = []
        if cls == Profession:
            rez = [cls._with_id(data) for data in db_adapter.get(UtilTypes.PROFESSION, _id=_id)]
        elif cls == Worker:
            for data in db_adapter.get(UtilTypes.WORKER, _id=_id):
                w_id, name, prof_id = data
                prof = Profession.from_db(_id=prof_id)
                rez.append(cls._with_id((w_id, name, prof)))

        elif cls == Blank:
            for data in db_adapter.get(UtilTypes.BLANK, _id=_id):
                b_id, w_id, date, data = data
                worker = Worker.from_db(_id=w_id)
                rez.append(cls._with_id((b_id, date, data, worker)))
        return rez if not _id else rez[0]

    def dump(self):
        db_adapter.add(self)

    @classmethod
    def _with_id(cls, arr):
        obj = cls(*arr[1:])
        obj.id = arr[0]
        return obj

    def db_del(self):
        db_adapter.delete(self)


class Profession(UtilSuperclass):

    def __init__(self, name, salary, min_hours):
        super().__init__()
        self.name = name
        self.salary = salary
        self.min_hours = min_hours


class Worker(UtilSuperclass):
    def __init__(self, name, profession):
        super().__init__()
        self.name = name
        self.profession = profession


class Blank(UtilSuperclass):

    def __init__(self, data, month, worker):
        super().__init__()
        self.data = data
        self.month = month
        self.worker = worker

from datetime import datetime, timedelta, date
from enum import Enum


class UtilTypes(Enum):
    PROFESSION = "professions",
    WORKER = "workers",
    BLANK = "blanks",


class Month(date):
    @classmethod
    def from_m_y(cls, month, year):
        return cls(month=month, year=year, day=28)

    def _last_day_of_month(self):
        next_month = self + timedelta(days=4)
        return next_month - timedelta(days=next_month.day)

    def __len__(self):
        return self._last_day_of_month().day

    def __str__(self):
        return f"{self.month}-{self.year}"

    @staticmethod
    def to_sqlite(month):
        return month.strftime("%Y%m")

    @classmethod
    def from_sqlite(cls, text):
        text = text.decode()
        dt = datetime.strptime(text, "%Y%m")
        return cls.from_m_y(dt.month, dt.year)


class HArray(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def to_sqlite(arr):
        return 'x'.join(map(str, arr))

    @classmethod
    def from_sqlite(cls, text):
        text = text.decode()
        return cls(map(lambda x: int(x) if x not in {"л","в"} else x, text.split('x')))

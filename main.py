from util import Profession, Worker, Blank
from db.db_types import HArray, Month
import logging
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    A = Profession("a", 1, 2)
    A.dump()
    A.name = "b"
    A.dump()


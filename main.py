from util import Profession, Worker, Blank
from db.db_types import HArray, Month
import logging
if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)
    p = Profession("prof", 10, 10)
    p.dump()
    w = Worker("work", p)
    w.dump()
    b = Blank(HArray([2]*28), Month.from_m_y(2, 2019), w)
    b.dump()

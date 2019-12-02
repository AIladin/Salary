import logging
import cgi
from db.util import Profession, Worker, Blank
from db.db_types import Month, HArray

MAIN_PAGE = "pages/main_page.html"
PROF_PAGE = "pages/prof_page.html"
with open("pages/prof_row_pattern.txt", 'r', encoding="utf-8") as f:
    PROF_PATT = f.read()
WORKER_PAGE = "pages/worker_page.html"
with open("pages/worker_row_pattern.txt", 'r', encoding="utf-8") as f:
    WORKER_PATT = f.read()
BLANK_PAGE = "pages/blank_page.html"
with open("pages/blank_row_pattern.txt", 'r', encoding="utf-8") as f:
    BLANK_PATT = f.read()
CALC_PAGE = "pages/calc_page.html"
with open("pages/calc_pattern.txt", 'r', encoding="utf-8") as f:
    CALC_PATT = f.read()


class SalaryServer:
    def __init__(self):
        self.commands = {"": self.start,
                         "show_main": self.start,
                         "show_professions": self.professions,
                         "change_prof": self.change_prof,
                         "del_prof": self.del_prof,
                         "show_workers": self.workers,
                         "change_worker": self.change_worker,
                         "del_worker": self.del_worker,
                         "show_blanks": self.blanks,
                         "change_blank": self.change_blank,
                         "del_blank": self.del_blank,
                         "show_calc": self.calcs,
                         }

    def __call__(self, environ, start_response):
        """Викликається WSGI-сервером.

           Отримує оточення environ та функцію,
           яку треба викликати у відповідь: start_response.
           Повертає відповідь, яка передається клієнту.
        """
        command = environ.get('PATH_INFO', '').lstrip('/')
        logging.info("Command: %s ", command)
        # отримати словник параметрів, переданих з HTTP-запиту
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
        err = False
        if command in self.commands:
            # виконати команду та отримати тіло відповіді
            body = self.commands[command](form)
            if body:
                start_response('200 OK', [('Content-Type',
                                           'text/html; charset=utf-8')])
            else:
                # якщо body - порожній рядок, то виникла помилка
                err = True
        else:
            # якщо команда невідома, то виникла помилка
            err = True
        if err:
            start_response('404 NOT FOUND', [('Content-Type',
                                              'text/plain; charset=utf-8')])
            body = 'Сторінку не знайдено'
        return [bytes(body, encoding='utf-8')]

    def start(self, form):
        with open(MAIN_PAGE, encoding='utf-8') as f:
            table = "\n".join([f"<option value='{worker.id}'>{worker.name}</value>" for worker in Worker.from_db()])
            cnt = f.read().format(table)
        return cnt

    def professions(self, form):
        with open(PROF_PAGE, encoding='utf-8') as f:
            cnt = f.read()
            table = ""
            for prof in Profession.from_db():
                table += PROF_PATT.format(prof.id, prof.name, prof.min_hours, prof.salary)
            table += """<form method="post">
                        <tr><td></td>
                        <td><input type="text" value="" name="name"></td>
                        <td><input type="text" value="" size=25 name="min_h" maxlength="3"></td>
                        <td><input type="text" value="" name="salary"></td>
                        <td><input type="submit" value="Додати" formaction="change_prof"></td>
                     """
        return cnt.format(table)

    def change_prof(self, form):
        p_id = form.getfirst("id", "")
        if p_id:
            p_id = int(p_id)
            prof = Profession.from_db(p_id)
        else:
            prof = Profession("", 0, 0)
        try:
            prof.name = form.getfirst("name", "")
            min_h = int(form.getfirst("min_h", ""))
            prof.min_hours = min_h if min_h<672 else 672
            prof.salary = int(form.getfirst("salary", ""))
            prof.dump()
        except:
            logging.warning("Input format error go on working.")
        return self.professions(form)

    def del_prof(self, form):
        p_id = int(form.getfirst("id", ""))
        prof = Profession.from_db(p_id)
        prof.db_del()
        return self.professions(form)

    def workers(self, form):
        with open(WORKER_PAGE, encoding='utf-8') as f:
            cnt = f.read()
            table = ""
            for worker in Worker.from_db():
                select = "<select name='p_id'>" +\
                         "\n".join([f"<option ' value='{prof.id}' " + (" selected>"
                                    if prof.name == worker.profession.name else ">")
                                    + prof.name + "</option>" for prof in Profession.from_db()]) +\
                         "</select>"

                table += WORKER_PATT.format(worker.id, worker.name, select)

            table += """<form method="post">
                            <td></td>
                            <td><input type="text" value="" name="name"></td>""" + \
                     "\n<td><select name='p_id'>" + \
                     "\n".join([f"<option value='{prof.id}'>" + prof.name + "</option>"
                                for prof in Profession.from_db()]) + \
                     "</select></td>\n" +\
                     """
                        <td><input type="submit" value="Додати" formaction="change_worker"></td>
                        </form>
                     """

        return cnt.format(table)

    def change_worker(self, form):
        w_id = form.getfirst("id", "")
        if w_id:
            w_id = int(w_id)
            worker = Worker.from_db(w_id)
        else:
            worker = Worker("", None)
        try:
            worker.name = form.getfirst("name", "")
            worker.profession = Profession.from_db(int(form.getfirst("p_id", "")))
            worker.dump()
        except:
            logging.warning("Wrong input go on working")
        return self.workers(form)

    def del_worker(self, form):
        w_id = int(form.getfirst("id", ""))
        worker = Worker.from_db(w_id)
        worker.db_del()
        return self.workers(form)

    @staticmethod
    def _get_workers_select(_id=None):
        rez = "<select name='worker_id'>"
        for worker in Worker.from_db():
            rez += f"<option value='{worker.id}'" + ("selected" if worker.id == _id else "") +\
                   f">{worker.name}</option>"
        return rez + "</select>"

    @staticmethod
    def _blank_row_gen(data):
        return "\n".join([f"<td><input type='text' value='{data[i] if i<len(data) else ''}'"
                          f" maxlength='2' size='2' name='day_{i}'></td>"
                         for i in range(31)])

    def blanks(self, form):
        with open(BLANK_PAGE, 'r', encoding='utf-8') as f:
            cnt = f.read()
        table = ""
        for blank in Blank.from_db():
            table += BLANK_PATT.format(blank.id, blank.month,
                                       self._get_workers_select(blank.worker.id),
                                       self._blank_row_gen(blank.data))

        table += """
        <form method="post">
        <tr>
            <td></td>
            <td><input type="text" value="01-2000" size=4 name="date" maxlength=8></td>
            <td>
            {}
            </td>
            {}
            <td><input type="submit" value="Додати" formaction="change_blank"></td>
        </tr>
    </form>
        """.format(self._get_workers_select(), self._blank_row_gen([""]*31))

        return cnt.format(table)

    def change_blank(self, form: cgi.FieldStorage):
        b_id = form.getfirst("id", "")
        if b_id:
            b_id = int(b_id)
            blank = Blank.from_db(b_id)
        else:
            blank = Blank(None, None, None)
        try:
            month = Month.from_m_y(*map(int, form.getfirst("date", "").split("-")))
            data = HArray()
            for day in range(len(month)):
                cell = form.getfirst(f"day_{day}")
                if cell.isdigit():
                    cell = int(cell)
                    if not 0 < cell < 24:
                        raise ValueError(f"Wrong cell literal {cell}")

                elif cell not in {"л", "в"}:
                    raise ValueError(f"Wrong cell literal {cell}")
                data.append(cell)
            w_id = int(form.getfirst("worker_id", ""))
            worker = Worker.from_db(w_id)
            blank.worker = worker
            blank.month = month
            blank.data = data
            blank.dump()
        except:
            logging.warning("Wrong input go on working.")
        return self.blanks(form)

    def del_blank(self, form: cgi.FieldStorage):
        b_id = int(form.getfirst("id", ""))
        blank = Blank.from_db(b_id)
        blank.db_del()
        return self.blanks(form)

    def calcs(self, form: cgi.FieldStorage):
        calc_type = form.getfirst("calc", "")
        try:
            if calc_type == "Робітник":
                month = Month.from_m_y(*map(int, form.getfirst("date", "").split("-")))
                return self._month_calc(month)
            else:
                worker = Worker.from_db(int(form.getfirst('worker_id', "")))
                b_month = Month.from_m_y(*map(int, form.getfirst("begin_date", "").split("-")))
                e_month = Month.from_m_y(*map(int, form.getfirst("end_date", "").split("-")))
                return self._worker_calc(worker, b_month, e_month)
        except:
            logging.warning("Wrong input working on.")
            return self.start(form)

    def _month_calc(self, month):
        with open(CALC_PAGE, "r", encoding='utf-8') as f:
            cnt = f.read()
        table = ""
        rez_s = 0
        for blank in Blank.from_db():
            if blank.month == month:
                s = (blank.data.hours_worked() if blank.data.hours_worked() < blank.worker.profession.min_hours
                     else blank.worker.profession.min_hours)*blank.worker.profession.salary +\
                     blank.data.mean()*blank.data.vacation() + 8/10*blank.data.ill()*blank.worker.profession.salary
                rez_s += s
                color = "#DAF7A6"
                if blank.data.hours_worked() < blank.worker.profession.min_hours:
                    color = "#FF5733"
                table += CALC_PATT.format(color,
                                          blank.worker.name,
                                          blank.data.hours_worked(),
                                          blank.worker.profession.min_hours,
                                          blank.data.vacation(),
                                          blank.data.ill(),
                                          s)
        return cnt.format(f"Місяць {month}", "Робітник", table, rez_s)

    def _worker_calc(self, worker, b_month, e_month):
        with open(CALC_PAGE, "r", encoding='utf-8') as f:
            cnt = f.read()
        table = ""
        rez_s = 0
        for blank in Blank.from_db():
            if blank.worker == worker and b_month < blank.month < e_month:
                s = (blank.data.hours_worked() if blank.data.hours_worked() < blank.worker.profession.min_hours
                     else blank.worker.profession.min_hours) * blank.worker.profession.salary + \
                    blank.data.mean() * blank.data.vacation() +\
                    8 / 10 * blank.data.ill() * blank.worker.profession.salary
                rez_s += s
                color = "#DAF7A6"
                if blank.data.hours_worked() < blank.worker.profession.min_hours:
                    color = "#FF5733"
                table += CALC_PATT.format(color,
                                          blank.month,
                                          blank.data.hours_worked(),
                                          blank.worker.profession.min_hours,
                                          blank.data.vacation(),
                                          blank.data.ill(),
                                          s)
        return cnt.format(f"Робітник: {worker.name}.      Посада:{worker.profession.name}.", "Місяць", table, rez_s)


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    print('=== Local WSGI web server ===')
    httpd = make_server('localhost', 8051, SalaryServer())
    host, port = httpd.server_address
    print(f"http://localhost:{port}")
    logging.basicConfig(level=logging.INFO,
                        format=f'{host} - - [%(asctime)s] %(levelname)s %(message)s',
                        datefmt='%d/%b/%Y %H:%M:%S')
    httpd.serve_forever()

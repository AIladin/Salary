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
                        <td><input type="text" value="" name="min_h" maxlength="3"></td>
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


if __name__ == '__main__':
    if __name__ == '__main__':
        from wsgiref.simple_server import make_server
        print('=== Local WSGI webserver ===')
        httpd = make_server('localhost', 8051, SalaryServer())
        host, port = httpd.server_address
        print(f"http://localhost:{port}")
        logging.basicConfig(level=logging.INFO,
                            format=f'{host} - - [%(asctime)s] %(levelname)s %(message)s',
                            datefmt='%d/%b/%Y %H:%M:%S')
        httpd.serve_forever()





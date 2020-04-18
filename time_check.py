import datetime as dt


class TimeContextManager():
    def __init__(self):
        self.current_time = dt.datetime.today()

    def __enter__(self):
        print('Начало работы программы -', self.current_time.strftime('%H:%M:%S'))

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = dt.datetime.today()
        print('Конец работы программы -', self.end_time.strftime('%H:%M:%S'))
        self.time_worked = self.end_time - self.current_time
        print('Время работы программы -', self.time_worked)
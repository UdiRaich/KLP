import time
from threading import Lock


class Container:
    def __init__(self, interval_value=1, unit='seconds'):

        if unit == 'seconds':
            self.__interval = interval_value
        elif unit == 'minutes':
            self.__interval = interval_value * 60
        elif unit == 'hours':
            self.__interval = interval_value * 3600
        elif unit == 'days':
            self.__interval = interval_value * 86400
        else:
            raise ValueError("Invalid unit. Choose from 'seconds', 'minutes', 'hours', 'days'.")

        self.__last_updated_time = None
        self.__container = []
        self._lock = Lock()

    def add(self, data):
        now = time.time()

        with self._lock:
            if self.__last_updated_time is None:
                self.__last_updated_time = now
                self.__container.append([now, []])

            elapsed = now - self.__last_updated_time

            if elapsed >= self.__interval:
                self.__last_updated_time = now
                self.__container.append([now, []])

            self.__container[-1][1].append(data)

    def pop_ready(self):
        with self._lock:
            if len(self.__container) <= 1:
                return []
            ready = self.__container[:-1]
            self.__container = self.__container[-1:]
            return ready

    def flush(self):
        with self._lock:
            data, self.__container = self.__container, []
            return data

import time
from threading import Lock
from utils.conversions_utils import convert_to_seconds


class Container:
    def __init__(self, interval_value, unit):
        self.__interval = convert_to_seconds(interval_value, unit)
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

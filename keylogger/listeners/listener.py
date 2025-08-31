from pynput import keyboard

from listeners.base import IListener


class Listener(IListener):
    def __init__(self, container, esc_callback):
        self._listener = None
        self._container = container
        self._esc_callback = esc_callback

    def on_press(self, key):
        if key == keyboard.Key.esc:
            self._esc_callback()
        else:
            self._container.add(key)

    def start(self):
        self._listener = keyboard.Listener(on_press=self.on_press)
        self._listener.start()

    def stop(self):
        self._listener.stop()

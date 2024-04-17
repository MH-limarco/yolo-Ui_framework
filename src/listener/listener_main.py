from pynput import mouse, keyboard
import multiprocessing, win32gui, win32con, win32api, time, ctypes
from ctypes import wintypes, WINFUNCTYPE

class Listener:
    def __init__(self, _shared, _event):
        self.shared_dict = _shared['dict_press']
        self.event_listener = _event['listener']

        self.key_listener = keyboard.Listener(on_press=self.on_press,
                                         on_release=self.on_release)

        self.mouse_listener = mouse.Listener(on_click=self.on_click)

    def on_press(self, key):
        if key not in self.shared_dict or not self.shared_dict[key]:
            self.shared_dict[key] = True
            self.activate()

    def on_release(self, key):
        if key in self.shared_dict.keys():
            self.shared_dict[key] = False
            self.activate()

    def on_click(self, x, y, button, pressed):
        self.shared_dict[f'mouse_{button.name}'] = pressed
        self.activate()

    def activate(self):
        self.event_listener.set()
        self.event_listener.clear()

    def output(self):
        return self.shared_dict, self.event_listener

    def start(self):
        self.key_listener.start()
        self.mouse_listener.start()

    def stop(self):
        self.key_listener.stop()
        self.mouse_listener.stop()

    def run(self):
        self.key_listener.start()
        self.mouse_listener.start()
        self.mouse_listener.join()

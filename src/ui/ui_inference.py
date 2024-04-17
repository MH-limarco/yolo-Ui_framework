import tkinter as tk
import ctypes
from ctypes import wintypes
import win32gui, win32con, win32api
import time

import random
import keyboard
import pyWinhook as pyHook
import numpy as np

from keyboard._keyboard_event import KEY_DOWN, KEY_UP

import ctypes
WIN_EVENT_CALLBACK_TYPE = ctypes.WINFUNCTYPE(
    None,
    ctypes.wintypes.HANDLE,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.HWND,
    ctypes.wintypes.LONG,
    ctypes.wintypes.LONG,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD
)

setting_dict = {'hwnd': win32gui.FindWindow(None, 'Webex'),
                'show': True}

class Box:
    def __init__(self, canvas, xyxy, width=2, outline = 'red'):
        self.rect = canvas.create_rectangle(xyxy[0], xyxy[1], xyxy[2], xyxy[3],
                                            width=width, outline = outline)

class App_inference(tk.Tk):
    def __init__(self, _shared, _event):
        super().__init__()
        self.wh = [[], []]
        self.event_run = _event['running']
        self.event_inference = _event['inference']

        self.setting_dict = _shared['dict_app']

        self.boxs_memory = _shared['boxes_memory']
        self.offset_memory = _shared['offset_memory']
        self.boxes_narray = np.ndarray(buffer=self.boxs_memory[0].buf, **self.boxs_memory[1])
        self.offset_narray = np.ndarray(buffer=self.offset_memory[0].buf, **self.offset_memory[1])

        self.title(str(random.randint(0, 1e5)))
        self.overrideredirect(True)
        self.config(bg='white')
        self.attributes("-alpha", 1)
        self.wm_attributes("-topmost", 1)
        self.attributes('-transparentcolor', 'white', '-topmost', 1)
        self.resizable(False, False)

        self.withdraw()
        self.set_hooks()
        self.canvas = tk.Canvas(self,
                                borderwidth=1,
                                bg='white')

        self.canvas.grid(sticky='nsew')

        self.update_position(self.setting_dict['hwnd'])
        self.start = time.perf_counter()
        self.after(1, self.updata_boxes)

    def callback(self, hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
        if hwnd == self.setting_dict['hwnd']:
            if event == win32con.EVENT_OBJECT_DESTROY:
                self.setting_dict['show'] = False
                self.show()

            elif self.setting_dict['show']:
                self.setting_dict['show'] = True
                self.update_position(hwnd)

    def set_hooks(self):
        self.callback_ptr = WIN_EVENT_CALLBACK_TYPE(self.callback)

        self.hook_start = ctypes.windll.user32.SetWinEventHook(
            win32con.EVENT_OBJECT_LOCATIONCHANGE,
            win32con.EVENT_OBJECT_LOCATIONCHANGE,
            0,
            self.callback_ptr,  # 使用转换后的函数指针
            0,
            0,
            win32con.WINEVENT_OUTOFCONTEXT
        )

        self.hook_destroy = ctypes.windll.user32.SetWinEventHook(
            win32con.EVENT_OBJECT_DESTROY,
            win32con.EVENT_OBJECT_DESTROY,
            0,
            self.callback_ptr,  # 使用转换后的函数指针
            0,
            0,
            win32con.WINEVENT_OUTOFCONTEXT
        )

    def update_position(self, hwnd):
        self.show()
        rect = win32gui.GetWindowRect(hwnd)
        left, top, right, bottom = rect
        wh = [right - left, bottom - top]
        if self.wh != wh:
            self.wh = wh
            self.geometry(f'{wh[0]}x{wh[1]}')

            self.canvas.config(width=wh[0], height=wh[1])


        self.geometry(f'+{left}+{top}')

    def show(self):
        if self.setting_dict['show']:
            self.deiconify()
        else:
            self.withdraw()

    def updata_boxes(self):
        self.event_inference.wait()
        print(1/(time.perf_counter() - self.start))
        self.start = time.perf_counter()
        self.canvas.delete("all")
        self.boxes_narray_ = self.boxes_narray[~np.all(self.boxes_narray == -1, axis=1)]

        [Box(self.canvas, coords) for coords in self.boxes_narray_+ self.offset_narray]
        if self.event_run.is_set():
            self.after(1, self.updata_boxes)

    def on_closing(self):
        self.destroy()
        try:
            ctypes.windll.user32.UnhookWinEvent(self.hook_start)
            ctypes.windll.user32.UnhookWinEvent(self.hook_destroy)
        except:
            pass
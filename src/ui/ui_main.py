import tkinter as tk
from tkinter import ttk
from ui_inference import App_infereence
import win32gui

class TkApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.sub_tk = {'frame':False}

        self.buttonA = ttk.Button(self, text="Create Frame", command=self.create_frame)
        self.buttonA.pack(pady=10)

        self.buttonB = ttk.Button(self, text="Close Frame", command=self.close_frame)
        self.buttonB.pack(pady=10)

    def create_frame(self):
        if not self.sub_tk['frame']:
            self.sub_tk['frame'] = True
            setting_dict = {'hwnd': win32gui.FindWindow(None, 'Webex')
                            ,'show': True}
            self.new_window = App_infereence(setting_dict, None, None, None)

            self.new_frame = ttk.Frame(self.new_window)
            self.new_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    def close_frame(self):
        if hasattr(self, "new_window"):
            self.sub_tk['frame'] = False
            self.new_window.on_closing()


app = TkApp()
app.mainloop()
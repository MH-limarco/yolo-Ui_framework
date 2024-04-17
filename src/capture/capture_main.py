from windows_capture import WindowsCapture, Frame, InternalCaptureControl
from multiprocessing.shared_memory import SharedMemory
from pynput.keyboard import Key
import numpy as np
import multiprocessing, threading, cv2

class Capture:
    def __init__(self, window_name, _shared, _event):
        self.crop_size = 1024
        self.capture = WindowsCapture(window_name=window_name)
        self.shared_dict = _shared['dict_press']

        self.event_run = _event['running']
        self.event_run.set()

        self.event_listener = _event['listener']
        self.event_capture = _event['capture']

        image_memory = _shared['image_memory']
        offset_memory = _shared['offset_memory']
        narray = np.ndarray(buffer=image_memory[0].buf, **image_memory[1])
        narray_offset = np.ndarray(buffer=offset_memory[0].buf, **offset_memory[1])

        self.thread = threading.Thread(target=self.read_listener)
        lock = threading.Lock()

        @self.capture.event
        def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
            frame = frame.convert_to_bgr().frame_buffer #.crop(0, 0, 1920, 1080)
            dimension = np.array(frame.shape[:-1][::-1])
            offset = np.tile((dimension // 2) - (self.crop_size // 2), 2)

            frame = frame[offset[1]:offset[1]+self.crop_size, offset[0]:offset[0]+self.crop_size]
            with lock:
                np.copyto(narray, frame)
                np.copyto(narray_offset, offset)

            self.event_capture.set()
            self.event_capture.clear()

            if not self.event_run.is_set():
                capture_control.stop()

        @self.capture.event
        def on_closed():
            pass

    def read_listener(self):
        while self.event_run.is_set():
            self.event_listener.wait()
            if Key.down in self.shared_dict:
                self.event_run.clear()
                print('stop')

    def output(self):
        return self.memory, self.event_capture, self.event_run

    def start(self):
        self.capture.start_free_threaded()
        self.thread.start()

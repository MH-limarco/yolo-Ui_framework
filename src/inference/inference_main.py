from ultralytics import YOLO
import numpy as np
import threading, cv2
from multiprocessing.shared_memory import SharedMemory
import multiprocessing

model = YOLO(f"../runs/train/CrowdHuman-base-v8n/weights/best.pt", task='detect')
model.fuse()
#print(model)
# window_name, _shared, _event
class Inference:
    def __init__(self, _shared, _event): #boxes_memory
        self.model = model
        self.show = True

        self.event_run = _event['running']
        self.event_capture = _event['capture']
        self.event_inference = _event['inference']

        self.image_memory = _shared['image_memory']
        self.boxes_memory = _shared['boxes_memory']

        self.narray_image = np.ndarray(buffer=self.image_memory[0].buf, **self.image_memory[1])
        self.narray_box = np.ndarray(buffer=self.boxes_memory[0].buf, **self.boxes_memory[1])

        self.thread = threading.Thread(target=self.core)

    def core(self):
        while self.event_run.is_set():
            self.event_capture.wait()
            self.pred()

    def pred(self):
        results = self.model(self.narray_image,
                             half=True,
                             conf=0.25,
                             iou=0.7,
                             imgsz=1024,
                             #agnostic_nms=False,
                             verbose=False
                             )[0]

        boxes = results.boxes

        if self.show:
            cv2.imshow('', results.plot())
            cv2.waitKey(1)

        _len = 0
        if len(boxes):
            body = boxes[boxes.cls==1].xyxy.cpu().numpy()
            _len = len(body)
            if _len > 0:
                self.narray_box[:_len] = body
        self.narray_box[_len:] = -1

        self.event_inference.set()
        self.event_inference.clear()

    def output(self):
        return self.boxes_memory, self.event_inference

    def start(self):
        self.thread.start()

    def stop(self):
        self.event_run.clear()
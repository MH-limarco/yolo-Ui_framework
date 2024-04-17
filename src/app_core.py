from src import *
from multiprocessing.shared_memory import SharedMemory
window_name = 'Apex Legends' #"Apex Legends"#"Battlefield™ 2042"  #'Webex'

image_dtype = np.uint8
image_shape = (1024, 1024, 3)

boxes_dtype = np.float32
boxes_shape = (300,4)

offset_dtype = np.int32
offset_shape = (4,)



image_setting = {'shape':image_shape,
                  'dtype':image_dtype}

boxes_setting = {'shape':boxes_shape,
                  'dtype':boxes_dtype}

offset_setting = {'shape':offset_shape,
                  'dtype':offset_dtype}


app_setting = {'hwnd': win32gui.FindWindow(None, window_name),
                'show': True}

shared_dict = {'dict_press':{},
             'dict_app':app_setting,
             'offset_memory':offset_setting,
             'image_memory':image_setting,
             'boxes_memory':boxes_setting}

event_dict = {'running', 'listener', 'capture', 'inference'}

def build_shared_memory(shape, dtype):
    shared_memory = SharedMemory(create=True,
                             size=int(np.prod(shape) * np.dtype(dtype).itemsize))
    return shared_memory

def get_ready(shared_dict, event_dict):
    _shared, _event = {}, {}
    for name, args in shared_dict.items():
        _type, _name = name.split('_')
        if _type == 'dict':
            _shared[name] = multiprocessing.Manager().dict(**args)
        else:
            _shared[name] = [build_shared_memory(**args), args]

    for name in event_dict:
        _event[name] = multiprocessing.Event()

    return _shared, _event

def app_core():
    _shared, _event = get_ready(shared_dict, event_dict)

    listener = Listener(_shared, _event)
    capture = Capture(window_name, _shared, _event)
    inference = Inference(_shared, _event)

    app_inference = App_inference(_shared, _event)

    listener.start()
    capture.start()
    inference.start()

    app_inference.mainloop()





if __name__ == '__main__':
    app_core()


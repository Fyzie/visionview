import numpy as np
import importlib
from PySide6.QtCore import QObject, Signal, Slot, QThread

_CV_MODULE_CACHE = {}

def get_cv_module(script_name):
    mod = _CV_MODULE_CACHE.get(script_name)
    if mod is None:
        mod = importlib.import_module(f"computer_vision.{script_name}")
        _CV_MODULE_CACHE[script_name] = mod
    return mod

class ImageWorker(QObject):
    image_ready = Signal(np.ndarray, int, int)
    finished = Signal()

    def __init__(self, image_array):
        super().__init__()
        self.image = image_array
        self.pipeline = []
        self._running = True

    @Slot()
    def process(self):
        try:
            orig_h, orig_w = self.image.shape[:2]
            while self._running:
                img = self.image.copy()
                for step in list(self.pipeline):
                    module_name = step.get('name', '')
                    params = step.get('params', {})
                    try:
                        script_name = module_name.lower().replace(" ", "_")
                        m = get_cv_module(script_name)
                        img = m.process(img, params)
                    except Exception as e:
                        print(f"Pipeline Error ({module_name}): {e}")
                
                curr_h, curr_w = img.shape[:2]
                self.image_ready.emit(img, curr_w, curr_h)
                
                # Control the frame rate (approx 33ms = 30fps)
                QThread.msleep(33)
        except Exception as e:
            print(f"ImageWorker error: {e}")
        finally:
            self.finished.emit()

    def stop(self):
        self._running = False
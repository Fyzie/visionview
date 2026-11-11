from PySide6.QtCore import QObject, Signal
import numpy as np

class GuiSignal(QObject):
    closed_module = Signal(object)
    enlarge_module = Signal(object, bool)
    module_selected = Signal(object)
    update_active_cameras = Signal(str)
    
gui_signal = GuiSignal()
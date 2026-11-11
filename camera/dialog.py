import os
import importlib
import inspect
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, 
                             QComboBox, QDialogButtonBox, QMessageBox)
from PySide6.QtCore import Qt

IGNORED_FILES = ["__init__.py", "dialog.py", "camera_worker.py","image_worker.py", "camera_parameters.py"]

class CameraInitDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Initialize Camera")
        self.window_module = parent
        self.selected_camera_instance = None
        self.selected_device = None

        self.layout = QVBoxLayout(self)
        self.form = QFormLayout()

        # 1. Camera Type Combobox
        self.type_combo = QComboBox()
        # self.type_combo.addItem("Select Type...")
        self.type_combo.currentIndexChanged.connect(self.on_type_selected)

        # 2. Camera Version (Serial Number) Combobox
        self.version_combo = QComboBox()
        self.version_combo.setEnabled(False)

        self.form.addRow("Camera Type:", self.type_combo)
        self.form.addRow("Camera Version:", self.version_combo)
        self.layout.addLayout(self.form)

        # 3. Buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setStyleSheet("""
            QDialog {
                background-color: #f6f7f9;
                border: none;
            }

            QLabel {
                background: none;
                border: none;
                font-size: 13px;
            }

            QComboBox QAbstractItemView {
                padding: 5px;
                border: 1px solid #c8c8c8;
                border-radius: 4px;
                background: white;
            }

            QComboBox {
                background-color: white;
                color: black;
                border: 1px solid #c8c8c8;
                selection-background-color: #409eff;
                selection-color: white;
            }
                           
            QComboBox:hover {
                border: 1px solid #409eff;
            }

            QPushButton {
                background: white;
                min-width: 80px;
                padding: 6px;
                border: 1px solid #c8c8c8;
                border-radius: 4px;
            }

            QPushButton:hover {
                background-color: #e6f2ff;
            }
            """)

        self.load_camera_scripts()
        if self.type_combo.count() > 0:
            self.on_type_selected(0)

    def load_camera_scripts(self):
        """Scans the 'camera' folder for .py files."""
        camera_dir = os.path.dirname(__file__)
        if not os.path.exists(camera_dir) and getattr(sys, 'frozen', False):
            base = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            alt_dir = os.path.join(base, "camera")
            if os.path.exists(alt_dir):
                camera_dir = alt_dir

        if os.path.exists(camera_dir):
            for filename in os.listdir(camera_dir):
                is_code = filename.endswith(".py") or filename.endswith(".pyc")
                stem = filename.replace(".pyc", "").replace(".py", "")
                if is_code and stem not in [ig.replace(".py", "") for ig in IGNORED_FILES]:
                    if self.type_combo.findData(stem) == -1:
                        self.type_combo.addItem(stem.capitalize(), stem)

        # Fallback for frozen executable if filesystem listing is unavailable
        if self.type_combo.count() == 0:
            self.type_combo.addItem("Basler", "basler")

    def on_type_selected(self, index):
        if index < 0:
            self.version_combo.clear()
            self.version_combo.setEnabled(False)
            return

        module_name = self.type_combo.currentData()
        try:
            # Dynamically import the module from the camera folder
            module = importlib.import_module(f"camera.{module_name}")
            
            # Find the class inside (e.g., Basler class in basler.py)
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__module__ == f"camera.{module_name}":
                    self.selected_camera_instance = obj() # Instantiate
                    break

            if self.selected_camera_instance:
                # Call the 'find()' method from your script
                devices, serials = self.selected_camera_instance.find()
                self.version_combo.clear()
                
                valid_count = 0
                if devices and serials:
                    main_win = getattr(self.window_module, 'main_window', self.window_module) if self.window_module else None
                    active_cams = getattr(main_win, 'active_cameras', []) if main_win else []
                    for dev, sn in zip(devices, serials):
                        sn_str = str(sn)
                        if sn_str in active_cams:  # Only list inactive cameras
                            continue
                        self.version_combo.addItem(sn_str, dev)
                        valid_count += 1

                if valid_count > 0:
                    self.version_combo.setEnabled(True)
                else:
                    msg = "No available devices" if devices else "No devices found"
                    self.version_combo.addItem(msg)
                    self.version_combo.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load {module_name}: {str(e)}")

    def validate_and_accept(self):
        if self.version_combo.currentIndex() < 0 or not self.version_combo.isEnabled():
            QMessageBox.warning(self, "Selection Required", "Please select a valid camera.")
            return
        
        self.selected_device = self.version_combo.currentData()
        self.selected_sn = self.version_combo.currentText() 
        if not self.selected_device or not self.selected_sn:
            QMessageBox.warning(self, "Selection Required", "Please select a valid camera.")
            return
        self.accept()
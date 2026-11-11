# scripts to generate parameter dialog for computer vision modules
from PySide6.QtWidgets import (QDialog, QFormLayout, QCheckBox, QSpinBox,
                               QDoubleSpinBox, QPushButton, QComboBox,
                               QWidget, QHBoxLayout, QLineEdit, QFileDialog,
                               QDialogButtonBox)
from PySide6.QtCore import Signal

from .deep_learning import get_ai_scripts

class ParameterDialog(QDialog):
    parametersChanged = Signal(dict)
    
    def __init__(self, title, params_def, current_values, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle(f"{title} Parameters")
        self.layout = QFormLayout(self)
        self.setMinimumWidth(350)
        self.widgets = {}
        self.params_def = params_def

        for name, config in params_def.items():
            label_text = name.replace("_", " ").title()
            current_val = current_values.get(name, config.get("default"))

            if config["type"] == "enum":
                w = QComboBox()
                w.addItems(config["options"])
                
                w.setCurrentText(str(current_val))
                
                w.currentTextChanged.connect(self.emit_updates)
                
                self.layout.addRow(label_text, w)
                self.widgets[name] = w

            elif config["type"] == "ai_modules":
                w = QComboBox()
                w.addItems(get_ai_scripts())
                
                w.setCurrentText(str(current_val))
                
                w.currentTextChanged.connect(self.emit_updates)
                
                self.layout.addRow(label_text, w)
                self.widgets[name] = w

            elif config["type"] == "int":
                spin = QSpinBox()
                spin.setRange(config.get("min", 0), config.get("max", 100))
                
                spin.setSingleStep(config.get("step", 1))
                
                spin.setValue(int(current_val))
                spin.valueChanged.connect(self.emit_updates)
                self.layout.addRow(label_text, spin)
                self.widgets[name] = spin
                
            elif config["type"] == "float":
                f_spin = QDoubleSpinBox()
                decimals = config.get("decimals", 2)
                f_spin.setDecimals(decimals)
                f_spin.setRange(config.get("min", 0.0), config.get("max", 100.0))
                f_spin.setSingleStep(config.get("step", 0.1))
                f_spin.setValue(float(current_val))
                f_spin.valueChanged.connect(self.emit_updates)
                self.layout.addRow(label_text, f_spin)
                self.widgets[name] = f_spin

            elif config["type"] == "bool":
                check = QCheckBox()
                check.setChecked(bool(current_val))
                check.toggled.connect(self.emit_updates)
                self.layout.addRow(label_text, check)
                self.widgets[name] = check

            elif config["type"] == "dir":
                container = QWidget()
                h_layout = QHBoxLayout(container)
                h_layout.setContentsMargins(0, 0, 0, 0)
                
                line_edit = QLineEdit(str(current_val))
                btn_browse = QPushButton("...")
                btn_browse.setFixedWidth(30)
                
                h_layout.addWidget(line_edit)
                h_layout.addWidget(btn_browse)
                
                # define the browse callback
                def browse(le, n):
                    dir_path = QFileDialog.getExistingDirectory(
                        self, 
                        "Select Folder",
                        le.text() or ""
                    )
                    if dir_path:
                        le.setText(dir_path)

                btn_browse.clicked.connect(lambda _, le=line_edit, n=name: browse(le, n))
                line_edit.textChanged.connect(self.emit_updates)
                
                self.layout.addRow(label_text, container)
                self.widgets[name] = line_edit

        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        self.button_box.accepted.connect(self.accept)
        self.layout.addRow(self.button_box)

    def get_values(self):
        result = {}
        for name, widget in self.widgets.items():
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                result[name] = widget.value()
            elif isinstance(widget, QComboBox):
                result[name] = widget.currentText()
            elif isinstance(widget, QCheckBox):
                result[name] = widget.isChecked()
            elif isinstance(widget, QLineEdit):
                result[name] = widget.text()
        return result

    def emit_updates(self):
        """Emits the current state of all widgets immediately"""
        self.parametersChanged.emit(self.get_values())
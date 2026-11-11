import os
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QListWidget,
    QHBoxLayout, QLabel, QMessageBox
)
from PySide6.QtCore import QFileSystemWatcher, Qt, QUrl
from PySide6.QtGui import QDesktopServices

class DirectoryViewer(QWidget):
    def __init__(self, directory, parent=None):
        super().__init__(parent)

        self.directory = directory
        Path(self.directory).mkdir(parents=True, exist_ok=True)

        layout = QVBoxLayout(self)

        # --- Open Explorer ---
        self.btn_open = QPushButton("Open File Explorer")
        self.btn_open.clicked.connect(self.open_explorer)

        # --- Delete / Clear Buttons ---
        btn_layout = QHBoxLayout()

        self.btn_delete = QPushButton("Delete")
        self.btn_delete.clicked.connect(self.delete_selected)

        self.btn_clear = QPushButton("Clear")
        self.btn_clear.clicked.connect(self.clear_folder)

        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_clear)

        # --- File Count ---
        self.file_count_label = QLabel("Number of files: 0")

        # --- File List ---
        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.open_image)

        # --- Layout ---
        layout.addWidget(self.btn_open)
        layout.addLayout(btn_layout)
        layout.addWidget(self.file_count_label)
        layout.addWidget(self.file_list)

        # --- Watch directory changes ---
        self.watcher = QFileSystemWatcher()
        if Path(self.directory).exists():
            self.watcher.addPath(self.directory)
        self.watcher.directoryChanged.connect(self.update_file_list)

        self.update_file_list()

    def update_file_list(self):
        """Refresh file list"""
        self.file_list.clear()

        path = Path(self.directory)

        if not path.exists():
            self.file_count_label.setText("Number of files: 0")
            return

        try:
            files = [f for f in path.iterdir() if f.is_file() and f.name.lower() != "desktop.ini"]
            files.sort(key=lambda x: x.stat().st_mtime if x.exists() else 0, reverse=True)

            count = 0
            for f in files:
                self.file_list.addItem(f.name)
                count += 1

            self.file_count_label.setText(f"Number of files: {count}")
            self.file_list.scrollToTop() # auto-scroll to the newest image every update
        except Exception as e:
            print(f"Error updating file list: {e}")

    def delete_selected(self):
        """Delete selected file with confirmation"""
        item = self.file_list.currentItem()

        if not item:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{item.text()}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        file_path = Path(self.directory) / item.text()

        try:
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to delete file: {e}")

        self.update_file_list()

    def clear_folder(self):
        """Delete all media files in folder with confirmation"""
        path = Path(self.directory)

        if not path.exists():
            return

        reply = QMessageBox.question(
            self, "Confirm Clear All",
            f"Are you sure you want to delete all files in '{self.directory}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        try:
            for f in path.iterdir():
                if f.is_file() and f.name.lower() != "desktop.ini":
                    f.unlink()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to clear folder: {e}")

        self.update_file_list()

    def open_image(self, item):
        """Open image or video directly when double clicked"""
        path = Path(self.directory) / item.text()
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def open_explorer(self):
        """Open OS file explorer"""
        Path(self.directory).mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.directory))
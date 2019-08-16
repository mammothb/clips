from datetime import datetime

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import (QComboBox, QHBoxLayout, QInputDialog, QLabel,
                             QLineEdit, QListWidget, QPushButton, QTextEdit,
                             QVBoxLayout, QWidget)

class ClipsView(QWidget):
    button_add_sig = pyqtSignal()
    button_browse_sig = pyqtSignal()
    button_create_sig = pyqtSignal()
    button_load_sig = pyqtSignal()
    button_preview_sig = pyqtSignal()
    button_remove_sig = pyqtSignal()
    button_save_sig = pyqtSignal()
    button_upload_sig = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.vbox = QVBoxLayout()
        self.name_labels = []
        self._init_browse_ui()
        self._init_option_ui()
        self._init_preset_ui()
        self._init_info_ui()

        self.setLayout(self.vbox)
        self.setContentsMargins(0, 0, 0, 0)

    def update_combo_box(self, presets):
        self._combo_box_preset.clear()
        self._combo_box_preset.addItem("Select preset")
        for item in presets:
            self._combo_box_preset.addItem(item)

    def update_file_names(self, file_names):
        self._list_widget_file_names.clear()
        self._list_widget_file_names.addItems(file_names)

    def remove_current_file_name(self):
        self._list_widget_file_names.takeItem(
            self._list_widget_file_names.currentRow())

    def request_preset_name(self):
        return QInputDialog.getText(self, "Save preset",
                                    "Enter preset name:")

    # =================================================================
    # On-click
    # =================================================================
    def button_add_clicked(self):
        self.button_add_sig.emit()

    def button_browse_clicked(self):
        self.button_browse_sig.emit()

    def button_create_clicked(self):
        self.button_create_sig.emit()

    def button_load_clicked(self):
        self.button_load_sig.emit()

    def button_preview_clicked(self):
        self.button_preview_sig.emit()

    def button_remove_clicked(self):
        self.button_remove_sig.emit()

    def button_save_clicked(self):
        self.button_save_sig.emit()

    def button_upload_clicked(self):
        self.button_upload_sig.emit()

    # =================================================================
    # Getters
    # =================================================================
    def get_current_combo_box_text(self):
        return self._combo_box_preset.currentText()

    def get_current_file_name(self):
        return self._list_widget_file_names.currentItem().text()

    def get_duration(self):
        return self._line_edit_duration.text()

    def get_end_time(self):
        return self._line_edit_end_time.text()

    def get_num_clip(self):
        return self._line_edit_num_clip.text()

    def get_start_time(self):
        return self._line_edit_start_time.text()

    # =================================================================
    # Setters
    # =================================================================
    def set_duration(self, text):
        return self._line_edit_duration.setText(text)

    def set_end_time(self, text):
        return self._line_edit_end_time.setText(text)

    def set_info(self, text):
        self._text_edit.append("{:02d}:{:02d}:{:02d} - {}".format(
            datetime.now().hour, datetime.now().minute,
            datetime.now().second, text))
        self._text_edit.ensureCursorVisible()
        self._text_edit.moveCursor(QTextCursor.End)

    def set_num_clip(self, text):
        return self._line_edit_num_clip.setText(text)

    def set_start_time(self, text):
        return self._line_edit_start_time.setText(text)

    def set_validity(self, index, is_valid):
        if is_valid:
            self._list_widget_file_names.item(index).setForeground(Qt.black)
        else:
            self._list_widget_file_names.item(index).setForeground(Qt.red)

    # =================================================================
    # Initialize UI
    # =================================================================
    def _init_browse_ui(self):
        label_file_name = QLabel("File name: ")

        self._list_widget_file_names = QListWidget()
        self._list_widget_file_names.setFixedHeight(100)

        button_browse = QPushButton("Browse")
        button_browse.clicked.connect(self.button_browse_clicked)
        button_add = QPushButton("Add")
        button_add.clicked.connect(self.button_add_clicked)
        button_remove = QPushButton("Remove")
        button_remove.clicked.connect(self.button_remove_clicked)

        vbox = QVBoxLayout()
        vbox.addWidget(button_browse)
        vbox.addWidget(button_add)
        vbox.addWidget(button_remove)

        hbox = QHBoxLayout()
        hbox.addWidget(label_file_name)
        hbox.addWidget(self._list_widget_file_names)
        hbox.addLayout(vbox)

        for i in range(hbox.count()):
            hbox.setAlignment(hbox.itemAt(i).widget(), Qt.AlignTop)

        self.vbox.addLayout(hbox)

    def _init_option_ui(self):
        label_start_time = QLabel("Start time: ")
        self._line_edit_start_time = QLineEdit()

        label_end_time = QLabel("End time: ")
        self._line_edit_end_time = QLineEdit()

        label_duration = QLabel("Duration: ")
        self._line_edit_duration = QLineEdit()

        label_num_clip = QLabel("No. of clips: ")
        self._line_edit_num_clip = QLineEdit()

        button_preview = QPushButton("Preview")
        button_preview.clicked.connect(self.button_preview_clicked)

        hbox = QHBoxLayout()
        hbox.addWidget(label_start_time)
        hbox.addWidget(self._line_edit_start_time)
        hbox.addWidget(label_end_time)
        hbox.addWidget(self._line_edit_end_time)
        hbox.addWidget(label_duration)
        hbox.addWidget(self._line_edit_duration)
        hbox.addWidget(label_num_clip)
        hbox.addWidget(self._line_edit_num_clip)
        hbox.addWidget(button_preview)

        for i in range(hbox.count() - 1):
            hbox.itemAt(i).widget().setObjectName("option")

        self.vbox.addLayout(hbox)

    def _init_preset_ui(self):
        self._combo_box_preset = QComboBox()
        button_load = QPushButton("Load")
        button_load.clicked.connect(self.button_load_clicked)
        button_save = QPushButton("Save")
        button_save.clicked.connect(self.button_save_clicked)

        hbox = QHBoxLayout()
        hbox.addWidget(self._combo_box_preset)
        hbox.addWidget(button_load)
        hbox.addWidget(button_save)

        self.vbox.addLayout(hbox)

    def _init_info_ui(self):
        self._text_edit = QTextEdit()
        self._text_edit.setFixedHeight(80)
        self._text_edit.setReadOnly(True)
        button_create = QPushButton("Create")
        button_create.clicked.connect(self.button_create_clicked)
        button_upload = QPushButton("Upload")
        button_upload.clicked.connect(self.button_upload_clicked)

        vbox = QVBoxLayout()
        vbox.addWidget(button_create)
        vbox.addWidget(button_upload)

        hbox = QHBoxLayout()
        hbox.addWidget(self._text_edit)
        hbox.addLayout(vbox)

        for i in range(hbox.count()):
            hbox.setAlignment(hbox.itemAt(i).widget(), Qt.AlignTop)

        self.vbox.addLayout(hbox)

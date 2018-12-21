from datetime import datetime

from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QPushButton, QTextEdit, QVBoxLayout

class InfoWidgetGroup(object):
    def __init__(self, parent, layout):
        self._parent = parent
        self._layout = layout

        self._label_info = None
        self.init_ui()
        self.set_info("Program started")

    def init_ui(self):
        self._text_edit = QTextEdit()
        self._text_edit.setFixedHeight(80)
        self._text_edit.setReadOnly(True)
        button_create = QPushButton("Create")
        button_create.clicked.connect(self.create)
        button_upload = QPushButton("Upload")
        button_upload.clicked.connect(self.upload)

        self._layout.addWidget(self._text_edit)

        vbox = QVBoxLayout()
        vbox.addWidget(button_create)
        vbox.addWidget(button_upload)
        self._layout.addLayout(vbox)

    def create(self):
        self._parent.create()

    def upload(self):
        self._parent.upload()

    def set_info(self, text):
        self._text_edit.append("{:02d}:{:02d}:{:02d} - {}".format(
            datetime.now().hour, datetime.now().minute,
            datetime.now().second, text))
        self._text_edit.ensureCursorVisible()
        self._text_edit.moveCursor(QTextCursor.End)

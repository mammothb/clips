from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QLabel, QPushButton

class InfoWidgetGroup(object):
    def __init__(self, parent, layout):
        self._parent = parent
        self._layout = layout

        self._label_info = None
        self.init_ui()

    def init_ui(self):
        self._label_info = QLabel("Preview clip information")
        self._label_info.setFrameShape(QFrame.Panel)
        self._label_info.setLineWidth(1)
        self._label_info.setTextInteractionFlags(Qt.TextSelectableByMouse)
        button_create = QPushButton("Create")
        button_create.clicked.connect(self.create)
        button_upload = QPushButton("Upload")
        button_upload.clicked.connect(self.upload)

        self._layout.addWidget(self._label_info)
        self._layout.addWidget(button_create)
        self._layout.addWidget(button_upload)

    def create(self):
        self._parent.create()

    def upload(self):
        self._parent.upload()

    def set_info(self, text):
        self._label_info.setText(text)

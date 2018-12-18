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
        button_create = QPushButton("Create")
        button_create.clicked.connect(self.create)

        self._layout.addWidget(self._label_info)
        self._layout.addWidget(button_create)

    def create(self):
        self._parent.create()

    def set_info(self, text):
        self._label_info.setText(text)

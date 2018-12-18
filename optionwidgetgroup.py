import logging

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton

LOG = logging.getLogger("option")

class OptionWidgetGroup(object):
    def __init__(self, parent, layout):
        self._parent = parent
        self._layout = layout
        self._line_edit_start_time = None
        self._line_edit_duration = None
        self._line_edit_num_clip = None

        self.init_ui()

    def init_ui(self):
        label_start_time = QLabel("Start time: ")
        label_start_time.setObjectName("nameLabel")
        self._line_edit_start_time = QLineEdit()

        label_duration = QLabel("Duration: ")
        label_duration.setObjectName("nameLabel")
        self._line_edit_duration = QLineEdit()

        label_num_clip = QLabel("No. of clips: ")
        label_num_clip.setObjectName("nameLabel")
        self._line_edit_num_clip = QLineEdit()

        button_preview = QPushButton("Preview")
        button_preview.clicked.connect(self.preview_clip_info)

        self._layout.addWidget(label_start_time)
        self._layout.addWidget(self._line_edit_start_time)
        self._layout.addWidget(label_duration)
        self._layout.addWidget(self._line_edit_duration)
        self._layout.addWidget(label_num_clip)
        self._layout.addWidget(self._line_edit_num_clip)
        self._layout.addWidget(button_preview)

    def preview_clip_info(self):
        self._parent.set_options(self._line_edit_start_time.text(),
                                 self._line_edit_duration.text(),
                                 self._line_edit_num_clip.text())

    def get_start_time_text(self):
        return self._line_edit_start_time.text()

    def set_start_time(self, text):
        self._line_edit_start_time.setText(text)

    def set_duration(self, text):
        self._line_edit_duration.setText(text)

    def set_num_clip(self, text):
        self._line_edit_num_clip.setText(text)

import logging

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton

from utils import try_parse_int64, try_parse_time

LOG = logging.getLogger("option")

class OptionWidgetGroup(object):
    def __init__(self, parent, layout):
        self._parent = parent
        self._layout = layout
        self._line_edit_starttime = None
        self._line_edit_duration = None
        self._line_edit_num_clip = None

        self.starttime = None
        self.duration = None
        self.num_clip = None
        self.jump = None

        self._init_ui()

    def preview_clip_info(self, quiet=False):
        if not self._parent.is_valid_source():
            self._parent.update_info("ERROR: Invalid video file")
            LOG.error("Invalid video file")
            return False
        if len(self._line_edit_starttime.text().split(":")) != 3:
            self._parent.update_info("ERROR: Invalid start time")
            LOG.error("Invalid start time")
            return False

        self.starttime = try_parse_time(self._line_edit_starttime.text())
        if self.starttime is None:
            self._parent.update_info("ERROR: Invalid start time")
            LOG.error("Invalid start time")
            return False
        if self.starttime > self._parent.get_source_length():
            self._parent.update_info("ERROR: Start time exceeds video "
                                     "length")
            LOG.error("Start time exceeds video length")
            return False

        working_duration = self._parent.get_source_length() - self.starttime

        self.duration = try_parse_int64(self._line_edit_duration.text())
        if self.duration is None or self.duration > working_duration:
            self._parent.update_info("ERROR: Invalid duration")
            LOG.error("Invalid duration")
            return False

        self.num_clip = try_parse_int64(self._line_edit_num_clip.text())
        if (self.num_clip is None or self.num_clip <= 0 or
                self.num_clip * self.duration > working_duration):
            self._parent.update_info("ERROR: Invalid no. of clips")
            LOG.error("Invalid no. of clips")
            return False

        trailer_duration = self.num_clip * self.duration
        self.jump = working_duration // self.num_clip

        if not quiet:
            self._parent.update_info(
                "INFO: Creating a {}s trailer with {} clips, each {}s long "
                "taken every {}s".format(trailer_duration, self.num_clip,
                                         self.duration, self.jump))
        return True

    def get_starttime_text(self):
        return self._line_edit_starttime.text()

    def set_starttime(self, text):
        self._line_edit_starttime.setText(text)

    def set_duration(self, text):
        self._line_edit_duration.setText(text)

    def set_num_clip(self, text):
        self._line_edit_num_clip.setText(text)

    def _init_ui(self):
        label_starttime = QLabel("Start time: ")
        label_starttime.setObjectName("nameLabel")
        self._line_edit_starttime = QLineEdit()

        label_duration = QLabel("Duration: ")
        label_duration.setObjectName("nameLabel")
        self._line_edit_duration = QLineEdit()

        label_num_clip = QLabel("No. of clips: ")
        label_num_clip.setObjectName("nameLabel")
        self._line_edit_num_clip = QLineEdit()

        button_preview = QPushButton("Preview")
        button_preview.clicked.connect(self.preview_clip_info)

        self._layout.addWidget(label_starttime)
        self._layout.addWidget(self._line_edit_starttime)
        self._layout.addWidget(label_duration)
        self._layout.addWidget(self._line_edit_duration)
        self._layout.addWidget(label_num_clip)
        self._layout.addWidget(self._line_edit_num_clip)
        self._layout.addWidget(button_preview)

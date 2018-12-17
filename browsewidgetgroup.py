import logging
import os.path
import subprocess

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton

from filedialogwidget import FileDialogWidget

LOG = logging.getLogger("browse")

class BrowseWidgetGroup(object):
    def __init__(self, parent, layout):
        self._parent = parent
        self._layout = layout
        self._line_edit_filename = None

        self.source = None
        self.source_dir = None
        self.source_length = None
        self.is_valid_source = False

        self._init_ui()

    def _init_ui(self):
        label_filename = QLabel("Filename: ")
        label_filename.setObjectName("nameLabel")
        self._line_edit_filename = QLineEdit()
        button_browse = QPushButton("Browse")
        button_browse.clicked.connect(self._browse_for_file)

        self._layout.addWidget(label_filename)
        self._layout.addWidget(self._line_edit_filename)
        self._layout.addWidget(button_browse)

    def _browse_for_file(self):
        FileDialogWidget(self._line_edit_filename)
        if not self._line_edit_filename.text():
            return
        self.source = self._line_edit_filename.text()
        self.source_dir = os.path.dirname(self.source)
        cmd_ffprobe = ["ffprobe", "-v", "error", "-show_entries",
                       "format=duration", "-of",
                       "default=noprint_wrappers=1:nokey=1", self.source]
        process = subprocess.Popen(cmd_ffprobe, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        stdout, __ = process.communicate()
        try:
            self.is_valid_source = True
            self.source_length = round(float(stdout.decode("utf-8")))
            LOG.info("Valid source: %s; Source length: %s", self.source,
                     self.source_length)
        except (AttributeError, ValueError):
            self.is_valid_source = False
            self._parent.update_info("ERROR: Invalid video file")

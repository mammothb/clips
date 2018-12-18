import logging

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

        self.init_ui()

    def init_ui(self):
        label_filename = QLabel("Filename: ")
        label_filename.setObjectName("nameLabel")
        self._line_edit_filename = QLineEdit()
        button_browse = QPushButton("Browse")
        button_browse.clicked.connect(self.browse_for_file)

        self._layout.addWidget(label_filename)
        self._layout.addWidget(self._line_edit_filename)
        self._layout.addWidget(button_browse)

    def browse_for_file(self):
        FileDialogWidget(self._line_edit_filename)
        if not self._line_edit_filename.text():
            return
        self._parent.set_source(self._line_edit_filename.text())

import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QListWidget, QPushButton, QVBoxLayout

from filedialogwidget import FileDialogWidget

LOG = logging.getLogger("browse")

class BrowseWidgetGroup(object):
    def __init__(self, parent, layout):
        self._parent = parent
        self._layout = layout
        self._line_edit_file_name = None

        self.source = None
        self.source_dir = None
        self.source_length = None
        self.is_valid_source = False

        self.init_ui()

    def init_ui(self):
        label_file_name = QLabel("File name: ")
        label_file_name.setObjectName("nameLabel")

        self._list_widget_file_names = QListWidget()
        self._list_widget_file_names.setFixedHeight(100)
        button_browse = QPushButton("Browse")
        button_browse.clicked.connect(self.browse_for_file)
        button_add = QPushButton("Add")
        button_add.clicked.connect(self.add_files)
        button_remove = QPushButton("Remove")
        button_remove.clicked.connect(self.remove_current_file)

        self._layout.addWidget(label_file_name)
        self._layout.addWidget(self._list_widget_file_names)

        vbox = QVBoxLayout()
        vbox.addWidget(button_browse)
        vbox.addWidget(button_add)
        vbox.addWidget(button_remove)
        self._layout.addLayout(vbox)

    def browse_for_file(self):
        file_dialog = FileDialogWidget(self._list_widget_file_names)
        file_dialog.browse_for_files()
        if self._list_widget_file_names.count() == 0:
            return
        self._parent.set_sources(
            [(self._list_widget_file_names.item(i).text(), i)
             for i in range(self._list_widget_file_names.count())])

    def add_files(self):
        n = self._list_widget_file_names.count()
        file_dialog = FileDialogWidget(self._list_widget_file_names)
        new_files = file_dialog.add_files()
        if not new_files:
            return
        self._parent.add_sources([(file_name, i + n)
                                  for i, file_name in enumerate(new_files)])

    def remove_item(self, idx):
        self._list_widget_file_names.takeItem(idx)

    def remove_current_file(self):
        self._parent.remove_job(
            self._list_widget_file_names.currentItem().text())
        self._list_widget_file_names.takeItem(
            self._list_widget_file_names.currentRow())

    def set_valid(self, idx, is_valid=True):
        if not is_valid:
            self._list_widget_file_names.item(idx).setForeground(Qt.red)
        else:
            self._list_widget_file_names.item(idx).setForeground(Qt.black)

import logging
import os.path
import sys

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread
from PyQt5.QtWidgets import (QApplication, QFrame,
                             QHBoxLayout, QLabel, QMainWindow,
                             QPushButton, QVBoxLayout, QWidget)

from browsewidgetgroup import BrowseWidgetGroup
from ffmpegworker import FfmpegWorker
from optionwidgetgroup import OptionWidgetGroup
from presetwidgetgroup import PresetWidgetGroup

class ClipsApp(QMainWindow):
    command = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.target = None
        self.starttime = None
        self.duration = None
        self.num_clip = None
        self.jump = None
        self.target_dir = None
        self.video_length = None
        self.has_valid_video = False
        self.cwd = os.path.realpath(os.path.dirname(__file__))
        self.init_ui()
        self._set_style_sheet()

    def init_ui(self):
        button_width = 100
        widget_central = QWidget()
        self.setCentralWidget(widget_central)

        hbox_filedialog = QHBoxLayout()
        self._browse_group = BrowseWidgetGroup(self, hbox_filedialog)

        hbox_options = QHBoxLayout()
        self._option_group = OptionWidgetGroup(self, hbox_options)

        hbox_preset = QHBoxLayout()
        self._preset_group = PresetWidgetGroup(self, hbox_preset)

        self.label_info = QLabel("Preview clip information")
        self.label_info.setFrameShape(QFrame.Panel)
        self.label_info.setLineWidth(1)
        button_create = QPushButton("Create")
        button_create.setFixedWidth(button_width)
        button_create.clicked.connect(self.create)

        hbox_info = QHBoxLayout()
        hbox_info.addWidget(self.label_info)
        hbox_info.addWidget(button_create)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox_filedialog)
        vbox.addLayout(hbox_options)
        vbox.addLayout(hbox_preset)
        vbox.addLayout(hbox_info)

        widget_central.setLayout(vbox)

        self.show()

    def update_info(self, text):
        print(text)

    def preview_clip_info(self, quiet=False):
        return self._option_group.preview_clip_info(quiet)

    def get_starttime(self):
        return self._option_group.starttime

    def get_starttime_text(self):
        return self._option_group.get_starttime_text()

    def get_duration(self):
        return self._option_group.duration

    def get_num_clip(self):
        return self._option_group.num_clip

    def set_starttime(self, text):
        self._option_group.set_starttime(text)

    def set_duration(self, text):
        self._option_group.set_duration(text)

    def set_num_clip(self, text):
        self._option_group.set_num_clip(text)

    def is_valid_source(self):
        return self._browse_group.is_valid_source

    def get_source_length(self):
        return self._browse_group.source_length

    def create(self):
        self.preview_clip_info()
        args = [self.target, self.starttime, self.duration, self.num_clip,
                self.jump]
        self.label_info.setText("INFO: Running")
        self.command.emit(args)

    def _set_style_sheet(self):
        self.setStyleSheet("""
            QLabel#nameLabel {
                max-width: 55px;
                min-width: 55px;
                width: 55px;
            }
            QPushButton {
                max-width: 100px;
                min-width: 100px;
                width: 100px;
            }
        """)

    @pyqtSlot(str)
    def update_status(self, status):
        self.label_info.setText(status)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = QApplication(sys.argv)
    thread = QThread()
    thread.start()

    worker = FfmpegWorker()
    worker.moveToThread(thread)

    clips_app = ClipsApp()
    clips_app.command.connect(worker.start_work)

    worker.signal_status.connect(clips_app.update_status)

    sys.exit(app.exec_())

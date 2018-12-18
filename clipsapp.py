import logging
import sys

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QMainWindow,
                             QVBoxLayout, QWidget)

from browsewidgetgroup import BrowseWidgetGroup
from clipmaker import ClipMaker
from ffmpegworker import FfmpegWorker
from gfycatuploader import GfycatUploader, GfycatUploaderError
from infowidgetgroup import InfoWidgetGroup
from optionwidgetgroup import OptionWidgetGroup
from presetwidgetgroup import PresetWidgetGroup

class ClipsApp(QMainWindow):
    ffmpeg_create = pyqtSignal(dict)
    gfycat_upload = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._is_created = False
        self._clip_maker = ClipMaker()
        self.init_ui()
        self._set_style_sheet()

    def init_ui(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)

        hbox_filedialog = QHBoxLayout()
        self._browse_group = BrowseWidgetGroup(self, hbox_filedialog)

        hbox_options = QHBoxLayout()
        self._option_group = OptionWidgetGroup(self, hbox_options)

        hbox_preset = QHBoxLayout()
        self._preset_group = PresetWidgetGroup(self, hbox_preset)

        hbox_info = QHBoxLayout()
        self._info_group = InfoWidgetGroup(self, hbox_info)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox_filedialog)
        vbox.addLayout(hbox_options)
        vbox.addLayout(hbox_preset)
        vbox.addLayout(hbox_info)

        widget_central.setLayout(vbox)

        self.show()

    def check_options(self):
        success, __ = self._clip_maker.check_options()
        return success

    def save_preset(self, preset_name):
        success, info = self._clip_maker.save_options_as_preset(preset_name)
        if success:
            self._preset_group.update_combo_box()
        else:
            self._info_group.set_info(info)

    def create(self):
        self._is_created = False
        if self.check_options():
            args = self._clip_maker.get_options()
            self._info_group.set_info("INFO: Running")
            self.ffmpeg_create.emit(args)
        else:
            self._info_group.set_info("ERROR: Invalid configuration")

    def upload(self):
        if self._is_created:
            self._info_group.set_info("INFO: Uploading")
            self.gfycat_upload.emit(self._clip_maker.target)
        else:
            self._info_group.set_info("ERROR: Trailer not created")

    def get_presets(self):
        return self._clip_maker.get_presets()

    def set_source(self, source_path):
        success, info = self._clip_maker.set_source(source_path)
        if not success:
            self._info_group.set_info(info)

    def set_options(self, start_time, duration, num_clip):
        success, info = self._clip_maker.set_options(start_time, duration,
                                                     num_clip)
        if success:
            self._info_group.set_info(info)
        else:
            self._info_group.set_info("ERROR: {}".format(info))

    def set_options_with_preset(self, preset_name):
        success, info = self._clip_maker.set_options_with_preset(preset_name)
        if success:
            self._option_group.set_start_time(
                self._clip_maker.start_time_str)
            self._option_group.set_duration(str(self._clip_maker.duration))
            self._option_group.set_num_clip(str(self._clip_maker.num_clip))
            self._info_group.set_info(info)
        else:
            self._info_group.set_info("ERROR: {}".format(info))

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
        self._info_group.set_info(status)
        self._is_created = True

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = QApplication(sys.argv)

    ffmpeg_thread = QThread()
    ffmpeg_thread.start()
    ffmpeg_worker = FfmpegWorker()
    ffmpeg_worker.moveToThread(ffmpeg_thread)

    gfycat_thread = QThread()
    gfycat_thread.start()
    gfycat_uploader = GfycatUploader()
    gfycat_uploader.moveToThread(gfycat_thread)

    clips_app = ClipsApp()
    clips_app.ffmpeg_create.connect(ffmpeg_worker.start_work)
    clips_app.gfycat_upload.connect(gfycat_uploader.upload_from_file)

    ffmpeg_worker.signal_status.connect(clips_app.update_status)
    gfycat_uploader.signal_status.connect(clips_app.update_status)

    sys.exit(app.exec_())

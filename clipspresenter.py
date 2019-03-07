import logging
import os.path

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject

from message import ErrorMessage, InfoMessage, Message

LOG = logging.getLogger("ClipsPresenter")

class ClipsPresenter(QObject):
    ffmpeg_create_sig = pyqtSignal(dict)
    gfycat_upload_sig = pyqtSignal(list)

    def __init__(self, clips_view, file_dialog_view, model):
        super().__init__()
        self.clips_view = clips_view
        self.file_dialog_view = file_dialog_view
        self.model = model

        self.clips_view.update_combo_box(self.model.get_presets())

        self.clips_view.button_add_sig.connect(self.add_files)
        self.clips_view.button_browse_sig.connect(self.browse_for_file)
        self.clips_view.button_create_sig.connect(self.create)
        self.clips_view.button_load_sig.connect(self.set_options_with_preset)
        self.clips_view.button_preview_sig.connect(self.preview_clip_info)
        self.clips_view.button_save_sig.connect(self.save_preset)
        self.clips_view.button_remove_sig.connect(self.remove_current_file)
        self.clips_view.button_upload_sig.connect(self.upload)

    def add_files(self):
        file_names = self.file_dialog_view.browse_for_files()
        self.model.extend_file_names([name for name in file_names
                                      if name not in self.model.file_names])
        self.model.update_sources()
        self.update_file_names()

    def browse_for_file(self):
        self.model.clear_file_names()
        self.model.set_file_names(self.file_dialog_view.browse_for_files())
        self.model.update_sources()
        self.update_file_names()

    def connect_ffmpeg(self, ffmpeg):
        self.ffmpeg_create_sig.connect(ffmpeg)

    def connect_gfycat(self, gfycat):
        self.gfycat_upload_sig.connect(gfycat)

    def connect_status(self, signal):
        signal.connect(self.update_status)

    def create(self):
        success, info = self.model.create()
        if success:
            self.ffmpeg_create_sig.emit(self.model.get_options())
            self.clips_view.set_info(InfoMessage(info))
        else:
            self.clips_view.set_info(ErrorMessage(info))

    def preview_clip_info(self):
        self.set_options(self.clips_view.get_start_time(),
                         self.clips_view.get_duration(),
                         self.clips_view.get_num_clip())

    def remove_current_file(self):
        file_name = self.clips_view.get_current_file_name()
        try:
            self.model.remove_file_name(file_name)
            self.clips_view.remove_current_file_name()
        except ValueError:
            pass

    def save_preset(self):
        if not self.model.check_options():
            info_str = "Invalid preset"
            LOG.warning(info_str)
            self.clips_view.set_info(ErrorMessage(info_str))
            return

        preset_name, ok = self.clips_view.request_preset_name()
        if ok:
            success, info = self.model.save_preset(preset_name)
            if success:
                self.clips_view.update_combo_box(self.model.get_presets())
            else:
                self.clips_view.set_info(ErrorMessage(info))

    def set_options(self, start_time, duration, num_clip):
        if any(not option for option in [start_time, duration, num_clip]):
            self.clips_view.set_info(ErrorMessage("Missing options"))
            return
        results = self.model.set_options(start_time, duration, num_clip)
        for result in results:
            if result.index == -1:
                self.clips_view.set_info(ErrorMessage(result.info_str))
                break
            self.clips_view.set_validity(result.index, result.is_valid)
            message = "{} - {}".format(os.path.basename(result.source_path),
                                       result.info_str)
            if result.is_valid:
                self.clips_view.set_info(InfoMessage(message))
            else:
                self.clips_view.set_info(ErrorMessage(message))

    def set_options_with_preset(self):
        preset_name = (self.clips_view.get_current_combo_box_text()
                       .split(" - ")[0])
        success, info = self.model.get_preset_options(preset_name)
        if success:
            self.clips_view.set_start_time(info[0])
            self.clips_view.set_duration(info[1])
            self.clips_view.set_num_clip(info[2])
            self.set_options(*info)
        else:
            self.clips_view.set_info(ErrorMessage(info))

    def update_file_names(self):
        self.clips_view.update_file_names(self.model.file_names)

    @pyqtSlot(Message)
    def update_status(self, message):
        self.clips_view.set_info(message)
        if message == InfoMessage("Done"):
            self.model.set_is_created(True)

    def upload(self):
        if self.model.get_is_created():
            self.clips_view.set_info(InfoMessage("Uploading"))
            self.gfycat_upload_sig.emit([job.target
                                         for job in self.model.get_jobs()])
        else:
            self.clips_view.set_info(ErrorMessage("Trailer not created"))

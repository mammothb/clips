from configparser import ConfigParser
import math
import os.path
import re
import subprocess
import sys

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread
from PyQt5.QtWidgets import (QApplication, QComboBox, QInputDialog, QFrame,
                             QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                             QPushButton, QVBoxLayout, QWidget)

from ffmpegworker import FfmpegWorker
from filedialogwidget import FileDialogWidget

class ClipsApp(QMainWindow):
    command = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.target = None
        self.starttime = None
        self.duration = None
        self.jump = None
        self.target_dir = None
        self.video_length = None
        self.has_valid_video = False
        self.cwd = os.path.realpath(os.path.dirname(__file__))
        self.config_filename = os.path.join(self.cwd, "presets.ini")
        if not os.path.exists(self.config_filename):
            open(self.config_filename, "a").close()
        self.config = ConfigParser()
        self.config.read(self.config_filename)
        self.init_ui()

    def init_ui(self):
        button_width = 100
        label_width = 55
        widget_central = QWidget()
        self.setCentralWidget(widget_central)

        label_filename = QLabel("Filename: ")
        label_filename.setFixedWidth(label_width)
        self.line_edit_filename = QLineEdit()
        button_browse = QPushButton("Browse")
        button_browse.setFixedWidth(button_width)
        button_browse.clicked.connect(self.browse_for_file)

        hbox_filedialog = QHBoxLayout()
        hbox_filedialog.addWidget(label_filename)
        hbox_filedialog.addWidget(self.line_edit_filename)
        hbox_filedialog.addWidget(button_browse)

        label_starttime = QLabel("Start time: ")
        label_starttime.setFixedWidth(label_width)
        self.line_edit_starttime = QLineEdit()
        label_duration = QLabel("Duration: ")
        self.line_edit_duration = QLineEdit()
        label_proportion = QLabel("Proportion: ")
        self.line_edit_proportion = QLineEdit()
        button_preview = QPushButton("Preview")
        button_preview.setFixedWidth(button_width)
        button_preview.clicked.connect(self.preview_clip_info)

        hbox_arguments = QHBoxLayout()
        hbox_arguments.addWidget(label_starttime)
        hbox_arguments.addWidget(self.line_edit_starttime)
        hbox_arguments.addWidget(label_duration)
        hbox_arguments.addWidget(self.line_edit_duration)
        hbox_arguments.addWidget(label_proportion)
        hbox_arguments.addWidget(self.line_edit_proportion)
        hbox_arguments.addWidget(button_preview)

        self.combo_preset = QComboBox()
        self.update_combo_box()
        button_load = QPushButton("Load")
        button_load.setFixedWidth(button_width)
        button_load.clicked.connect(self.load_preset)
        button_save = QPushButton("Save")
        button_save.setFixedWidth(button_width)
        button_save.clicked.connect(self.save_preset)

        hbox_preset = QHBoxLayout()
        hbox_preset.addWidget(self.combo_preset)
        hbox_preset.addWidget(button_load)
        hbox_preset.addWidget(button_save)

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
        vbox.addLayout(hbox_arguments)
        vbox.addLayout(hbox_preset)
        vbox.addLayout(hbox_info)

        widget_central.setLayout(vbox)

        self.show()

    def browse_for_file(self):
        __ = FileDialogWidget(self.line_edit_filename)
        if not self.line_edit_filename.text():
            return
        self.target = self.line_edit_filename.text()
        self.target_dir = os.path.dirname(self.target)
        cmd_ffprobe = ["ffprobe", "-i", self.target]
        process = subprocess.Popen(cmd_ffprobe, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)

        stdout, __ = process.communicate()
        try:
            self.has_valid_video = True
            matches = re.search(r"Duration:\s{1}(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?),", str(stdout), re.DOTALL).groupdict()
            t_hh_sec = float(matches["hours"]) * 3600.0
            t_mm_sec = float(matches["minutes"]) * 60.0
            t_ss_sec = round(float(matches["seconds"]))

            self.video_length = t_hh_sec + t_mm_sec + t_ss_sec
        except AttributeError:
            self.has_valid_video = False
            self.label_info.setText("ERROR: Invalid video file")

    def preview_clip_info(self, quiet=False):
        if not self.has_valid_video:
            self.label_info.setText("ERROR: Invalid video file")
            return
        if try_parse_int64(self.line_edit_duration.text()) is None:
            self.label_info.setText("ERROR: Invalid duration")
            return
        if (try_parse_int64(self.line_edit_proportion.text()) is None or
                try_parse_int64(self.line_edit_proportion.text()) <= 0 or
                try_parse_int64(self.line_edit_proportion.text()) > 100):
            self.label_info.setText("ERROR: Invalid proportion")
            return
        if len(self.line_edit_starttime.text().split(":")) != 3:
            self.label_info.setText("ERROR: Invalid start time")
            return
        t_start = [try_parse_int64(t)
                   for t in self.line_edit_starttime.text().split(":")]
        t_hh_sec = float(t_start[0]) * 3600.0
        t_mm_sec = float(t_start[1]) * 60.0
        t_ss_sec = round(float(t_start[2]))

        total_sec = t_hh_sec + t_mm_sec + t_ss_sec
        if (t_start[0] < 0 or t_start[1] < 0 or t_start[2] < 0 or
                t_start[1] >= 60 or t_start[2] >= 60):
            self.label_info.setText("ERROR: Invalid start time")
            return
        if total_sec > self.video_length:
            self.label_info.setText("ERROR: Start time exceeds video length")
            return
        self.starttime = self.line_edit_starttime.text()
        self.duration = self.line_edit_duration.text()
        proportion = self.line_edit_proportion.text()

        working_duration = self.video_length - total_sec
        num_clips = int(math.ceil(100.0 * float(working_duration) /
                                  float(self.video_length) /
                                  float(try_parse_int64(proportion))))
        trailer_duration = float(num_clips) * try_parse_int64(self.duration)
        self.jump = int(float(try_parse_int64(proportion)) / 100.0 *
                        float(self.video_length))

        if not quiet:
            self.label_info.setText(
                "INFO: Creating a {}s trailer ".format(int(trailer_duration)) +
                "with {} clips, ".format(num_clips) +
                "each {}s long taken every {}s".format(self.duration,
                                                       self.jump))

    def create(self):
        self.preview_clip_info()
        outfilename = os.path.splitext(self.target)[0] + ".webm"
        select_arg = r"lt(mod(t\,{})\,{})".format(self.jump, self.duration)
        cmd = ["ffmpeg", "-ss", self.starttime, "-i", self.target,
               "-vf", "select='{}',setpts=N/FRAME_RATE/TB".format(select_arg),
               "-an", "-c:v", "libvpx-vp9", "-b:v", "3M", "-y", outfilename]
        self.label_info.setText("INFO: Running")

        with open(os.path.join(self.cwd, "debug.txt"), "w") as debug_file:
            debug_file.write(" ".join(cmd))
        self.command.emit(cmd)

    def update_combo_box(self):
        self.combo_preset.clear()
        self.combo_preset.addItem("Select preset")
        for section in self.config:
            if section != "DEFAULT":
                self.combo_preset.addItem(
                    "{} - Start time: {}; Duration: {}; Proportion: {}".format(
                        section, self.config[section]["starttime"],
                        self.config[section]["duration"],
                        self.config[section]["proportion"]))

    def load_preset(self):
        try:
            key = self.combo_preset.currentText().split(" - ")[0]
            if key == "Select preset":
                raise AttributeError
            self.line_edit_starttime.setText(self.config[key]["starttime"])
            self.line_edit_duration.setText(self.config[key]["duration"])
            self.line_edit_proportion.setText(self.config[key]["proportion"])
        except AttributeError:
            self.label_info.setText("ERROR: Invalid preset")

    def save_preset(self):
        self.preview_clip_info(quiet=True)
        preset_name, ok = QInputDialog.getText(self, "Choose a preset name",
                                               "Enter preset name:")
        if ok:
            self.config.add_section(preset_name)
            self.config[preset_name] = {
                "starttime": self.starttime,
                "duration": self.duration,
                "proportion": self.line_edit_proportion.text()
            }
            with open(self.config_filename, "w") as config_file:
                self.config.write(config_file)
        self.update_combo_box()

    @pyqtSlot(str)
    def update_status(self, status):
        self.label_info.setText(status)

def try_parse_int64(string):
    try:
        ret = int(string)
    except ValueError:
        return None
    return None if ret < -2 ** 64 or ret >= 2 ** 64 else ret

if __name__ == "__main__":
    app = QApplication(sys.argv)
    thread = QThread()
    thread.start()

    worker = FfmpegWorker()
    worker.moveToThread(thread)

    clips_app = ClipsApp()
    clips_app.command.connect(worker.start_work)

    worker.signal_status.connect(clips_app.update_status)

    sys.exit(app.exec_())

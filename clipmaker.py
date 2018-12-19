from configparser import ConfigParser, DuplicateSectionError
import logging
import os.path
import subprocess
import sys

from utils import try_parse_int64, try_parse_time

LOG = logging.getLogger("ClipMaker")

class ClipMaker(object):
    def __init__(self):
        self.source = None
        self.source_dir = None
        self.source_len = None
        self.is_valid_source = False
        self.target = None

        self.start_time_str = None
        self.start_time = None
        self.duration = None
        self.num_clip = None
        self.jump = None

        cwd = os.path.realpath(os.path.dirname(sys.argv[0]))
        self.config_filename = os.path.join(cwd, "presets.ini")
        open(self.config_filename, "a").close()
        self.config = ConfigParser()
        self.config.read(self.config_filename)

    def check_source(self):
        if self.source is None:
            self.is_valid_source = False
            info_str = "Invalid video file"
            LOG.warning(info_str)
            return False, info_str

        cmd_ffprobe = ["ffprobe", "-v", "error", "-show_entries",
                       "format=duration", "-of",
                       "default=noprint_wrappers=1:nokey=1", self.source]
        process = subprocess.Popen(cmd_ffprobe, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        stdout, __ = process.communicate()
        try:
            self.source_len = round(float(stdout.decode("utf-8")))
            self.is_valid_source = True
            self.target = os.path.splitext(self.source)[0] + ".webm"
            info_str = "Valid source: {}; Source length: {}".format(
                self.source, self.source_len)
            LOG.info(info_str)
            return True, info_str
        except (AttributeError, ValueError):
            self.is_valid_source = False
            info_str = "Invalid video file"
            LOG.warning(info_str)
            return False, info_str

    def check_options(self):
        success, info = self.check_source()
        if not success:
            return success, info
        if self.start_time is None:
            info_str = "Invalid start time"
            LOG.warning(info_str)
            return False, info_str
        if self.start_time > self.source_len:
            info_str = "Start time exceeds video length"
            LOG.warning(info_str)
            return False, info_str

        working_duration = self.source_len - self.start_time
        if (self.duration is None or self.duration <= 0 or
                self.duration > working_duration):
            info_str = "Invalid duration"
            LOG.warning(info_str)
            return False, info_str

        trailer_duration = self.num_clip * self.duration
        if (self.num_clip is None or self.num_clip <= 0 or
                trailer_duration > working_duration):
            info_str = "Invalid no. of clips"
            LOG.warning(info_str)
            return False, info_str

        self.jump = working_duration // self.num_clip
        info_str = ("Creating a {}s trailer with {} clips, each {}s long "
                    "taken every {}s".format(trailer_duration, self.num_clip,
                                             self.duration, self.jump))
        LOG.info(info_str)
        return True, info_str

    def save_options_as_preset(self, preset_name):
        try:
            self.config.add_section(preset_name)
            self.config[preset_name] = {
                "start_time": self.start_time_str,
                "duration": self.duration,
                "num_clip": self.num_clip
            }
            with open(self.config_filename, "w") as config_file:
                self.config.write(config_file)
            info_str = ("Saved preset '{}' - start_time: {}; duration: {}; "
                        "num_clip: {}".format(preset_name,
                                              self.start_time_str,
                                              self.duration,
                                              self.num_clip))
            LOG.info(info_str)
            return True, info_str
        except DuplicateSectionError:
            info_str = "Duplicate preset name"
            LOG.warning(info_str)
            return False, info_str

    def get_options(self):
        return {
            "source": self.source,
            "target": self.target,
            "start_time": self.start_time,
            "duration": self.duration,
            "num_clip": self.num_clip,
            "jump": self.jump
            }

    def get_presets(self):
        for section in self.config:
            if section != "DEFAULT":
                yield ("{} - Start time: {}; Duration: {}; No. of clips: "
                       "{}".format(section,
                                   self.config[section]["start_time"],
                                   self.config[section]["duration"],
                                   self.config[section]["num_clip"]))

    def set_source(self, source_path):
        self.source = source_path
        self.source_dir = os.path.dirname(source_path)
        return self.check_source()

    def set_options(self, start_time, duration, num_clip):
        self.start_time_str = start_time
        self.start_time = try_parse_time(start_time)
        self.duration = try_parse_int64(duration)
        self.num_clip = try_parse_int64(num_clip)
        return self.check_options()

    def set_options_with_preset(self, preset_name):
        try:
            if preset_name == "Select preset":
                raise AttributeError
            return self.set_options(self.config[preset_name]["start_time"],
                                    self.config[preset_name]["duration"],
                                    self.config[preset_name]["num_clip"])
        except AttributeError:
            info_str = "Invalid preset"
            LOG.warning(info_str)
            return False, info_str

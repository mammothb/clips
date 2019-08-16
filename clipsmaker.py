from collections import namedtuple
from configparser import ConfigParser, DuplicateSectionError
import logging
import os.path
import subprocess
import sys

from utils import try_parse_int64, try_parse_time

LOG = logging.getLogger("ClipMaker")

def check_source(source_path):
    cmd_ffprobe = ["ffprobe", "-v", "error", "-show_entries",
                   "format=duration,format_name", "-of",
                   "compact=print_section=0:nokey=1",
                   source_path]
    process = subprocess.Popen(cmd_ffprobe, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    stdout, __ = process.communicate()
    try:
        format_name, source_len_str = stdout.decode("utf-8").split("|")
        # Handle .txt files properly
        if format_name == "tty":
            raise ValueError
        source_len = round(float(source_len_str))
        target = os.path.splitext(source_path)[0] + ".webm"
        info_str = "Valid: {}; Length: {}".format(source_path, source_len)
        LOG.info(info_str)
        return True, target, source_len
    except (AttributeError, ValueError):
        info_str = "Invalid: {}".format(source_path)
        LOG.warning(info_str)
        return False, "", -1.0

class ClipJob(object):
    def __init__(self, source_path, target, source_length):
        self.is_valid = True
        self.jump = None
        self.source = source_path
        self.source_dir = os.path.dirname(source_path)
        self.source_length = source_length
        self.target = target

class ClipsMaker(object):
    def __init__(self):
        self.jobs = []

        self.start_time_str = None
        self.start_time = None
        self.end_time_str = None
        self.end_time = None
        self.duration = None
        self.num_clip = None
        self.jump = None

        self.config_file_name = os.path.join(
            os.path.realpath(os.path.dirname(sys.argv[0])), "presets.ini")
        open(self.config_file_name, "a").close()
        self.config = ConfigParser()
        self.config.read(self.config_file_name)

    def add_job(self, source_path, target, source_length):
        self.jobs.append(ClipJob(source_path, target, source_length))

    def check_options(self):
        if not self.jobs:
            return [Result(False, -1, "", "No source videos")]

        if self.start_time is None:
            info_str = "Invalid start time"
            LOG.warning(info_str)
            return [Result(False, -1, "", info_str)]
        if self.duration is None or self.duration <= 0:
            info_str = "Invalid duration"
            LOG.warning(info_str)
            return [Result(False, -1, "", info_str)]
        if self.num_clip is None or self.num_clip <= 0:
            info_str = "Invalid no. of clips"
            LOG.warning(info_str)
            return [Result(False, -1, "", info_str)]

        results = []
        for idx, job in enumerate(self.jobs):
            job.is_valid = False
            if self.end_time is None:
                working_duration = job.source_length - self.start_time
            else:
                working_duration = self.end_time - self.start_time
            trailer_duration = self.num_clip * self.duration
            if self.end_time and self.end_time > job.source_length:
                info_str = "Invalid end time"
                LOG.warning("%s: %s", info_str, job.source)
            elif self.duration > working_duration:
                info_str = "Invalid duration"
                LOG.warning("%s: %s", info_str, job.source)
            elif trailer_duration > working_duration:
                info_str = "Invalid no. of clips"
                LOG.warning("%s: %s", info_str, job.source)
            else:
                job.is_valid = True
                job.jump = working_duration // self.num_clip
                info_str = ("{}s trailer using {} x {}s clips, "
                            "taken every {}s".format(
                                trailer_duration, self.num_clip,
                                self.duration, job.jump))
            results.append(Result(job.is_valid, idx, job.source, info_str))
        return results

    def clear_jobs(self):
        self.jobs.clear()

    def save_options_as_preset(self, preset_name):
        try:
            self.config.add_section(preset_name)
            self.config[preset_name] = {
                "start_time": self.start_time_str,
                "end_time": self.end_time_str,
                "duration": self.duration,
                "num_clip": self.num_clip
            }
            with open(self.config_file_name, "w") as config_file:
                self.config.write(config_file)
            info_str = ("Saved preset '{}' - start_time: {}; end_time: {}; "
                        "duration: {}; num_clip: {}".format(
                            preset_name,
                            self.start_time_str,
                            self.end_time_str,
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
            "source": [job.source for job in self.jobs],
            "target": [job.target for job in self.jobs],
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "num_clip": self.num_clip,
            "jump": [job.jump for job in self.jobs]
        }

    def get_presets(self):
        for section in self.config:
            if section != "DEFAULT":
                yield ("{} - Start time: {}; End time: {}; Duration: {}; "
                       "No. of clips: {}".format(
                           section,
                           self.config[section]["start_time"],
                           self.config[section]["end_time"],
                           self.config[section]["duration"],
                           self.config[section]["num_clip"]))

    def get_preset_options(self, preset_name):
        try:
            if preset_name == "Select preset":
                raise AttributeError
            return True, (self.config[preset_name]["start_time"],
                          self.config[preset_name]["end_time"],
                          self.config[preset_name]["duration"],
                          self.config[preset_name]["num_clip"])
        except AttributeError:
            info_str = "Invalid preset"
            LOG.warning(info_str)
            return False, info_str

    def set_options(self, start_time_str, end_time_str, duration, num_clip):
        self.start_time_str = start_time_str
        self.start_time = try_parse_time(start_time_str)
        self.end_time_str = end_time_str
        self.end_time = try_parse_time(end_time_str)
        self.duration = try_parse_int64(duration)
        self.num_clip = try_parse_int64(num_clip)
        return self.check_options()

Result = namedtuple("Result", ["is_valid", "index", "source_path",
                               "info_str"])
Result.__new__.__defaults__ = (None,) * len(Result._fields)

from configparser import ConfigParser, DuplicateSectionError
import logging
import os.path
import subprocess
import sys

from utils import try_parse_int64, try_parse_time

LOG = logging.getLogger("ClipMaker")

def check_source(source_path):
    cmd_ffprobe = ["ffprobe", "-v", "error", "-show_entries",
                   "format=duration", "-of",
                   "default=noprint_wrappers=1:nokey=1", source_path]
    process = subprocess.Popen(cmd_ffprobe, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    stdout, __ = process.communicate()
    try:
        source_len = round(float(stdout.decode("utf-8")))
        is_valid = True
        target = os.path.splitext(source_path)[0] + ".webm"
        info_str = "Valid source: {}; Source length: {}".format(source_path,
                                                                source_len)
        LOG.info(info_str)
        return is_valid, target, source_len, info_str
    except (AttributeError, ValueError):
        is_valid = False
        info_str = "Invalid source: {}".format(source_path)
        LOG.warning(info_str)
        return is_valid, "", -1.0, info_str

class ClipJob(object):
    def __init__(self, source_path, target, source_length):
        self.is_valid = True
        self.jump = None
        self.source = source_path
        self.source_dir = os.path.dirname(source_path)
        self.source_length = source_length
        self.target = target

class ClipMaker(object):
    def __init__(self):
        self.jobs = []
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
        self.config_file_name = os.path.join(cwd, "presets.ini")
        open(self.config_file_name, "a").close()
        self.config = ConfigParser()
        self.config.read(self.config_file_name)

    def check_options(self):
        if not self.jobs:
            return [(False, "No source videos")]

        if self.start_time is None:
            info_str = "Invalid start time"
            LOG.warning(info_str)
            return [(False, -1, "", info_str)]
        if self.duration is None or self.duration <= 0:
            info_str = "Invalid duration"
            LOG.warning(info_str)
            return [(False, -1, "", info_str)]
        if self.num_clip is None or self.num_clip <= 0:
            info_str = "Invalid no. of clips"
            LOG.warning(info_str)
            return [(False, -1, "", info_str)]

        results = []
        for idx, job in enumerate(self.jobs):
            job.is_valid = False
            working_duration = job.source_length - self.start_time
            trailer_duration = self.num_clip * self.duration
            if self.duration > working_duration:
                info_str = "Invalid duration"
                LOG.warning("%s: %s", info_str, job.source)
                results.append((False, idx, job.source, info_str))
            elif trailer_duration > working_duration:
                info_str = "Invalid no. of clips"
                LOG.warning("%s: %s", info_str, job.source)
                results.append((False, idx, job.source, info_str))
            else:
                job.is_valid = True
                job.jump = working_duration // self.num_clip
                info_str = ("{}s trailer using {} x {}s clips, "
                            "taken every {}s".format(
                                trailer_duration, self.num_clip,
                                self.duration, job.jump))
                results.append((True, idx, job.source, info_str))
        return results

    def save_options_as_preset(self, preset_name):
        try:
            self.config.add_section(preset_name)
            self.config[preset_name] = {
                "start_time": self.start_time_str,
                "duration": self.duration,
                "num_clip": self.num_clip
            }
            with open(self.config_file_name, "w") as config_file:
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

    def add_sources(self, source_paths):
        results = []
        for source_path, idx in source_paths:
            info = check_source(source_path)
            if info[0]:
                self.jobs.append(ClipJob(source_path, info[1], info[2]))
            results.append((info[0], idx, source_path))
        return results

    def remove_job(self, source_path):
        for i, job in enumerate(self.jobs):
            if job.source == source_path:
                del self.jobs[i]
                break

    def get_options(self):
        return {
            "source": [job.source for job in self.jobs],
            "target": [job.target for job in self.jobs],
            "start_time": self.start_time,
            "duration": self.duration,
            "num_clip": self.num_clip,
            "jump": [job.jump for job in self.jobs]
            }

    def get_presets(self):
        for section in self.config:
            if section != "DEFAULT":
                yield ("{} - Start time: {}; Duration: {}; No. of clips: "
                       "{}".format(section,
                                   self.config[section]["start_time"],
                                   self.config[section]["duration"],
                                   self.config[section]["num_clip"]))

    def get_preset_options(self, preset_name):
        try:
            if preset_name == "Select preset":
                raise AttributeError
            return True, (self.config[preset_name]["start_time"],
                          self.config[preset_name]["duration"],
                          self.config[preset_name]["num_clip"])
        except AttributeError:
            info_str = "Invalid preset"
            LOG.warning(info_str)
            return False, info_str

    def set_sources(self, source_paths):
        results = []
        self.jobs.clear()
        for source_path, idx in source_paths:
            info = check_source(source_path)
            if info[0]:
                self.jobs.append(ClipJob(source_path, info[1], info[2]))
            results.append((info[0], idx, source_path))
        return results

    def set_options(self, start_time, duration, num_clip):
        self.start_time_str = start_time
        self.start_time = try_parse_time(start_time)
        self.duration = try_parse_int64(duration)
        self.num_clip = try_parse_int64(num_clip)
        return self.check_options()

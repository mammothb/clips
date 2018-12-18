import os
import os.path
import shutil
import subprocess

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject

class FfmpegWorker(QObject):
    signal_status = pyqtSignal(str)

    @pyqtSlot(dict)
    def start_work(self, args):
        source_name = args["source"]
        outfilename = args["target"]
        t_start_sec = args["start_time"]
        duration = str(args["duration"])
        num_clip = args["num_clip"]
        jump = args["jump"]

        src_dir = os.path.dirname(source_name)
        tmp_dir = os.path.normpath(os.path.join(src_dir, "tmp"))
        clip_file = os.path.normpath(os.path.join(tmp_dir, "cliplist.txt"))
        debug_file = os.path.normpath(os.path.join(tmp_dir, "debug.txt"))
        prefix, __ = os.path.splitext(os.path.basename(source_name))

        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)

        debug_file = open(debug_file, "w")
        with open(clip_file, "w") as outfile:
            for i in range(num_clip):
                file_name = os.path.normpath(os.path.join(
                    tmp_dir, "{}_{}{}".format(prefix, i, ".webm")))
                start_time = str(int(t_start_sec + i * jump))
                cmd = ["ffmpeg", "-fflags", "+genpts", "-loglevel", "error",
                       "-ss", start_time, "-i", source_name, "-t", duration,
                       "-c:v", "libvpx", "-b:v", "3M", "-an",
                       "-avoid_negative_ts", "1", "-y", file_name]
                subprocess.call(cmd)
                outfile.write("file '{}'\n".format(file_name))
                debug_file.write("{}\n".format(" ".join(cmd)))
        cmd = ["ffmpeg", "-fflags", "+genpts", "-f", "concat", "-safe", "0",
               "-i", clip_file, "-c:v", "libvpx", "-b:v", "3M", "-an",
               "-threads", "2", "-y", outfilename]
        debug_file.write("{}\n".format(" ".join(cmd)))
        debug_file.close()
        rc = subprocess.check_call(cmd)
        if not rc:
            shutil.rmtree(tmp_dir)

        self.signal_status.emit("INFO: Done")

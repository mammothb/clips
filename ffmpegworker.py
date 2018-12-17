import os
import os.path
import shutil
import subprocess

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject

from utils import try_parse_int64

class FfmpegWorker(QObject):
    signal_status = pyqtSignal(str)

    @pyqtSlot(list)
    def start_work(self, cmd):
        source_name = cmd[0]
        t_start = [try_parse_int64(t) for t in cmd[1].split(":")]
        duration = cmd[2]
        num_clip = try_parse_int64(cmd[3])
        jump = try_parse_int64(cmd[4])

        src_dir = os.path.dirname(source_name)
        tmp_dir = os.path.normpath(os.path.join(src_dir, "tmp"))
        clip_file = os.path.normpath(os.path.join(tmp_dir, "cliplist.txt"))
        debug_file = os.path.normpath(os.path.join(tmp_dir, "debug.txt"))
        prefix, extension = os.path.splitext(os.path.basename(source_name))
        outfilename = os.path.splitext(source_name)[0] + ".webm"

        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)

        t_hh_sec = float(t_start[0]) * 3600.0
        t_mm_sec = float(t_start[1]) * 60.0
        t_ss_sec = round(float(t_start[2]))

        t_start_sec = t_hh_sec + t_mm_sec + t_ss_sec
        debug_file = open(debug_file, "w")
        with open(clip_file, "w") as outfile:
            for i in range(num_clip):
                file_name = os.path.normpath(os.path.join(
                    tmp_dir, "{}_{}{}".format(prefix, i, extension)))
                start_time = int(t_start_sec + i * jump)
                cmd = ["ffmpeg", "-ss", str(start_time), "-i", source_name,
                       "-t", duration, "-c:v", "copy", "-an",
                       "-avoid_negative_ts", "1", "-y", file_name]
                subprocess.call(cmd)
                outfile.write("file '{}'\n".format(file_name))
                debug_file.write("{}\n".format(" ".join(cmd)))
        cmd = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", clip_file,
               "-c:v", "libvpx", "-b:v", "3M", "-an", "-threads", "2", "-y",
               outfilename]
        debug_file.write("{}\n".format(" ".join(cmd)))
        debug_file.close()
        rc = subprocess.check_call(cmd)
        if not rc:
            shutil.rmtree(tmp_dir)

        self.signal_status.emit('INFO: Done')

import os
import os.path
import shutil
import subprocess

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject

from message import InfoMessage, Message

class FfmpegWorker(QObject):
    status_sig = pyqtSignal(Message)

    @pyqtSlot(dict)
    def start_work(self, args):
        t_start_sec = args["start_time"]
        duration = str(args["duration"])
        num_clip = args["num_clip"]
        for i, source_name in enumerate(args["source"]):
            self.status_sig.emit(
                InfoMessage("Converting {}".format(source_name)))
            outfile_name = args["target"][i]
            jump = args["jump"][i]

            src_dir = os.path.dirname(source_name)
            tmp_dir = os.path.normpath(os.path.join(src_dir, "tmp"))
            clip_file = os.path.normpath(os.path.join(tmp_dir,
                                                      "cliplist.txt"))
            debug_file = os.path.normpath(os.path.join(tmp_dir, "debug.txt"))
            prefix, __ = os.path.splitext(os.path.basename(source_name))

            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)

            debug_file = open(debug_file, "w")
            with open(clip_file, "w") as outfile:
                for j in range(num_clip):
                    file_name = os.path.normpath(os.path.join(
                        tmp_dir, "{}_{}{}".format(prefix, j, ".webm")))
                    start_time = str(int(t_start_sec + j * jump))
                    cmd = ["ffmpeg", "-fflags", "+genpts", "-hide_banner",
                           "-ss", start_time, "-i", source_name, "-t",
                           duration, "-c:v", "libvpx", "-b:v", "3M", "-c:a",
                           "libvorbis", "-b:a", "128k", "-avoid_negative_ts",
                           "1", "-y", file_name]
                    subprocess.call(cmd)
                    outfile.write("file '{}'\n".format(file_name))
                    debug_file.write("{}\n".format(" ".join(cmd)))
            cmd = ["ffmpeg", "-fflags", "+genpts", "-hide_banner", "-f",
                   "concat", "-safe", "0", "-i", clip_file, "-c:v", "copy",
                   "-c:a", "copy", "-threads", "2", "-y", outfile_name]
            debug_file.write("{}\n".format(" ".join(cmd)))
            debug_file.close()
            rc = subprocess.check_call(cmd)
            if not rc:
                shutil.rmtree(tmp_dir)

        self.status_sig.emit(InfoMessage("Done"))

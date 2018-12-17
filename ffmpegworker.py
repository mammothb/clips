import subprocess

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject

class FfmpegWorker(QObject):
    signal_status = pyqtSignal(str)

    @pyqtSlot(list)
    def start_work(self, cmd):
        subprocess.call(cmd)
        self.signal_status.emit('INFO: Done')

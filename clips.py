import logging
import sys

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from clipsmodel import ClipsModel
from clipspresenter import ClipsPresenter
from clipsview import ClipsView
from filedialogview import FileDialogView
from ffmpegworker import FfmpegWorker
from gfycatuploader import GfycatUploader

class ClipsApp(QMainWindow):
    """Wrapper class for setting the main window"""
    def __init__(self, parent=None):
        super().__init__(parent)

        clips_model = ClipsModel()
        clips_view = ClipsView()
        file_dialog_view = FileDialogView()
        self.clips_presenter = ClipsPresenter(clips_view, file_dialog_view,
                                              clips_model)

        self.window = QMainWindow()

        vbox = QVBoxLayout()
        vbox.addWidget(clips_view)
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)

        widget_central = QWidget()
        widget_central.setLayout(vbox)
        self.setCentralWidget(widget_central)
        self.setWindowTitle("Clips maker")

        self._set_style_sheet()

    def connect_ffmpeg(self, ffmpeg):
        self.clips_presenter.connect_ffmpeg(ffmpeg)

    def connect_gfycat(self, gfycat):
        self.clips_presenter.connect_gfycat(gfycat)

    def connect_status(self, signal):
        self.clips_presenter.connect_status(signal)

    def _set_style_sheet(self):
        self.setStyleSheet("""
            QLabel#option {
                max-width: 55px;
                min-width: 55px;
                width: 55px;
            }
            QLineEdit#option {
                max-width: 60px;
                min-width: 60px;
                width: 60px;
            }
            QPushButton {
                max-width: 100px;
                min-width: 100px;
                width: 100px;
            }
        """)

def qapp():
    if QApplication.instance():
        _app = QApplication.instance()
    else:
        _app = QApplication(sys.argv)
    return _app

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = qapp()

    ffmpeg_thread = QThread()
    ffmpeg_thread.start()
    ffmpeg_worker = FfmpegWorker()
    ffmpeg_worker.moveToThread(ffmpeg_thread)

    gfycat_thread = QThread()
    gfycat_thread.start()
    gfycat_uploader = GfycatUploader()
    gfycat_uploader.moveToThread(gfycat_thread)

    window = ClipsApp()
    window.connect_ffmpeg(ffmpeg_worker.start_work)
    window.connect_status(ffmpeg_worker.status_sig)
    window.connect_gfycat(gfycat_uploader.upload_from_file)
    window.connect_status(gfycat_uploader.status_sig)
    window.show()

    app.exec_()

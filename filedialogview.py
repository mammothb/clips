from PyQt5.QtWidgets import QFileDialog, QWidget

class FileDialogView(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Browse for input file...")
        self.setGeometry(100, 100, 640, 480)

    def browse_for_files(self):
        options = QFileDialog.Options() | QFileDialog.DontUseNativeDialog
        return QFileDialog.getOpenFileNames(
            self, "Browse for video file", "", "All Files (*)",
            options=options)[0]

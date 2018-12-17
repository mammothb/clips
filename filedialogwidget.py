from PyQt5.QtWidgets import QFileDialog, QWidget

class FileDialogWidget(QWidget):
    def __init__(self, line_edit):
        super().__init__()
        self.init_ui()
        self.browse_for_file(line_edit)

    def init_ui(self):
        self.setWindowTitle("Browse for input file...")
        self.setGeometry(100, 100, 640, 480)

    def browse_for_file(self, line_edit):
        line_edit.setText("")
        options = QFileDialog.Options() | QFileDialog.DontUseNativeDialog
        file_name, __ = QFileDialog.getOpenFileName(
            self, "Browse for video file", "", "All Files (*)",
            options=options)
        if file_name:
            line_edit.setText(file_name)

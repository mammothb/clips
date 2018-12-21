from PyQt5.QtWidgets import QFileDialog, QWidget

class FileDialogWidget(QWidget):
    def __init__(self, list_widget):
        super().__init__()
        self._list_widget = list_widget
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Browse for input file...")
        self.setGeometry(100, 100, 640, 480)

    def browse_for_files(self):
        self._list_widget.clear()
        options = QFileDialog.Options() | QFileDialog.DontUseNativeDialog
        file_names, __ = QFileDialog.getOpenFileNames(
            self, "Browse for video file", "", "All Files (*)",
            options=options)
        if file_names:
            self._list_widget.addItems(file_names)

    def add_files(self):
        options = QFileDialog.Options() | QFileDialog.DontUseNativeDialog
        file_names, __ = QFileDialog.getOpenFileNames(
            self, "Browse for video file", "", "All Files (*)",
            options=options)
        new_files = []
        if file_names:
            existing_files = [self._list_widget.item(i).text()
                              for i in range(self._list_widget.count())]
            for file_name in file_names:
                if file_name not in existing_files:
                    self._list_widget.addItem(file_name)
                    new_files.append(file_name)
        return new_files

import logging

from PyQt5.QtWidgets import QComboBox, QInputDialog, QPushButton

LOG = logging.getLogger("preset")

class PresetWidgetGroup(object):
    def __init__(self, parent, layout):
        self._parent = parent
        self._layout = layout
        self._combo_box_preset = None

        self.init_ui()

    def init_ui(self):
        self._combo_box_preset = QComboBox()
        self.update_combo_box()
        button_load = QPushButton("Load")
        button_load.clicked.connect(self.load_preset)
        button_save = QPushButton("Save")
        button_save.clicked.connect(self.save_preset)

        self._layout.addWidget(self._combo_box_preset)
        self._layout.addWidget(button_load)
        self._layout.addWidget(button_save)

    def update_combo_box(self):
        self._combo_box_preset.clear()
        self._combo_box_preset.addItem("Select preset")
        for item in self._parent.get_presets():
            self._combo_box_preset.addItem(item)

    def load_preset(self):
        self._parent.set_options_with_preset(
            self._combo_box_preset.currentText().split(" - ")[0])

    def save_preset(self):
        if not self._parent.check_options():
            info_str = "Invalid preset"
            LOG.warning(info_str)
            self._parent.update_info("ERROR: {}".format(info_str))
            return

        preset_name, ok = QInputDialog.getText(
            self._parent, "Save preset", "Enter preset name:")
        if ok:
            self._parent.save_preset(preset_name)

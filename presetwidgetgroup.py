from configparser import ConfigParser, DuplicateSectionError
import logging
import os.path

from PyQt5.QtWidgets import QComboBox, QInputDialog, QPushButton

LOG = logging.getLogger("preset")

class PresetWidgetGroup(object):
    def __init__(self, parent, layout):
        self._parent = parent
        self._layout = layout
        self._combo_box_preset = None

        cwd = os.path.realpath(os.path.dirname(__file__))
        self.config_filename = os.path.join(cwd, "presets.ini")
        open(self.config_filename, "a").close()
        self.config = ConfigParser()
        self.config.read(self.config_filename)

        self._init_ui()

    def update_combo_box(self):
        self._combo_box_preset.clear()
        self._combo_box_preset.addItem("Select preset")
        for section in self.config:
            if section != "DEFAULT":
                self._combo_box_preset.addItem(
                    "{} - Start time: {}; Duration: {}; No. of clips: "
                    "{}".format(section,
                                self.config[section]["starttime"],
                                self.config[section]["duration"],
                                self.config[section]["numclip"]))
    def load_preset(self):
        try:
            key = self._combo_box_preset.currentText().split(" - ")[0]
            if key == "Select preset":
                raise AttributeError
            self._parent.set_starttime(self.config[key]["starttime"])
            self._parent.set_duration(self.config[key]["duration"])
            self._parent.set_num_clip(self.config[key]["numclip"])
        except AttributeError:
            self._parent.update_info("ERROR: Invalid preset")
            LOG.error("Invalid preset")

    def save_preset(self):
        if not self._parent.preview_clip_info(quiet=True):
            self._parent.update_info("ERROR: Invalid preset")
            LOG.error("Invalid preset")
            return
        preset_name, ok = QInputDialog.getText(self._parent,
                                               "Choose a preset name",
                                               "Enter preset name:")
        if ok:
            try:
                self.config.add_section(preset_name)
                self.config[preset_name] = {
                    "starttime": self._parent.get_starttime_text(),
                    "duration": self._parent.get_duration(),
                    "numclip": self._parent.get_num_clip()
                }
                with open(self.config_filename, "w") as config_file:
                    self.config.write(config_file)
            except DuplicateSectionError:
                self._parent.update_info("ERROR: Duplicate preset name")
                LOG.error("Duplicate preset name")
        self.update_combo_box()

    def _init_ui(self):
        self._combo_box_preset = QComboBox()
        self.update_combo_box()
        button_load = QPushButton("Load")
        button_load.clicked.connect(self.load_preset)
        button_save = QPushButton("Save")
        button_save.clicked.connect(self.save_preset)

        self._layout.addWidget(self._combo_box_preset)
        self._layout.addWidget(button_load)
        self._layout.addWidget(button_save)

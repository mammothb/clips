from clipsmaker import check_source, ClipsMaker

class ClipsModel(object):
    def __init__(self):
        self.maker = ClipsMaker()
        self.file_names = []
        self._is_created = False

    def update_sources(self):
        valid_file_names = []
        self.maker.clear_jobs()
        for file_name in self.file_names:
            is_valid, target, length = check_source(file_name)
            if is_valid and file_name not in valid_file_names:
                valid_file_names.append(file_name)
                self.maker.add_job(file_name, target, length)
        self.file_names = valid_file_names

    def check_options(self):
        return (all([job.is_valid for job in self.maker.jobs]) and
                self.maker.jobs)

    def clear_file_names(self):
        self.file_names.clear()

    def create(self):
        self._is_created = False
        if self.check_options():
            return True, "Running"
        else:
            return False, "Invalid configuration"

    def extend_file_names(self, file_names):
        self.file_names.extend(file_names)

    def remove_file_name(self, file_name):
        self.file_names.remove(file_name)

    def save_preset(self, preset_name):
        return self.maker.save_options_as_preset(preset_name)

    # =================================================================
    # Getters
    # =================================================================
    def get_is_created(self):
        return self._is_created

    def get_jobs(self):
        return self.maker.jobs

    def get_options(self):
        return self.maker.get_options()

    def get_presets(self):
        return self.maker.get_presets()

    def get_preset_options(self, preset_name):
        return self.maker.get_preset_options(preset_name)

    # =================================================================
    # Setters
    # =================================================================
    def set_file_names(self, file_names):
        self.file_names = file_names

    def set_is_created(self, is_created):
        self._is_created = is_created

    def set_options(self, start_time, end_time, duration, num_clip):
        return self.maker.set_options(start_time, end_time, duration,
                                      num_clip)

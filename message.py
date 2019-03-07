class Message(object):
    def __init__(self, message_type, message):
        self._message_type = message_type
        self._message = message

    def __eq__(self, other):
        return (self._message_type == other._message_type and
                self._message == other._message)

    def __str__(self):
        return "{}: {}".format(self._message_type, self._message)

class ErrorMessage(Message):
    def __init__(self, message):
        super().__init__("ERROR", message)

class InfoMessage(Message):
    def __init__(self, message):
        super().__init__("INFO", message)

class GfycatUploaderError(ErrorMessage):
    def __init__(self, error_message, status_code=None):
        if status_code:
            super().__init__("({}) {}".format(status_code, error_message))
        else:
            super().__init__(error_message)

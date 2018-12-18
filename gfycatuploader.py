import logging
import os.path
import time

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject
import requests

LOG = logging.getLogger("GfycatUploader")

class GfycatUploaderError(object):
    def __init__(self, error_message, status_code=None):
        self.status_code = status_code
        self.error_message = error_message

    def __str__(self):
        if self.status_code:
            return "({}) {}".format(self.status_code, self.error_message)
        else:
            return self.error_message

class GfycatUploader(QObject):
    api_endpoint = "https://api.gfycat.com/v1/gfycats"
    filedrop_endpoint = "https://filedrop.gfycat.com"
    status_endpoint = "https://api.gfycat.com/v1/gfycats/fetch/status"
    token_endpoint = "https://api.gfycat.com/v1/oauth/token"

    signal_status = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        cwd = os.path.realpath(os.path.dirname(__file__))
        with open(os.path.join(cwd, "apikey.txt"), "r") as api_file:
            self.client_id, self.client_secret = [
                s.split("=")[-1].strip() for s in api_file.readlines()]

    def emit_error(self, error_message, status_code=None):
        error = GfycatUploaderError(error_message, status_code)
        LOG.warning(error)
        self.signal_status.emit("ERROR: {}".format(error))

    def get_auth_headers(self):
        body = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        r = requests.post(self.token_endpoint, json=body, timeout=3)
        if r.status_code != 200:
            self.emit_error("Error requesting token", r.status_code)
            return None
        auth_headers = {
            "Authorization" : "Bearer {}".format(r.json()["access_token"])
        }
        return auth_headers

    @pyqtSlot(str)
    def upload_from_file(self, file_name):
        """Upload a local file to Gfycat. Taken from:
        https://gist.github.com/hellopatrick/ab6a9dfbbc7c1db7e6b817d06399fffd
        """
        gif_info = {
            "title": os.path.splitext(os.path.basename(file_name))[0],
            "noMd5": "true",
            "nsfw": 1
        }
        headers = self.get_auth_headers()
        if headers is None:
            return
        r = requests.post(self.api_endpoint, json=gif_info, headers=headers)
        if r.status_code != 200:
            self.emit_error("Error requesting ID", r.status_code)
            return
        gfyname = r.json()["gfyname"]
        LOG.info("Requested ID: %s", gfyname)
        with open(file_name, "rb") as source:
            r = requests.put("{}/{}".format(self.filedrop_endpoint, gfyname),
                             source)
            if r.status_code != 200:
                self.emit_error("Error uploading file", r.status_code)
                return
        LOG.info("Encoding")
        status = "encoding"
        wait_count = 0
        while status == "encoding":
            status = self.get_upload_status(gfyname)
            time.sleep(3)
            wait_count += 1
            if wait_count > 300:
                break
        if status != "complete":
            self.emit_error("Gfycat could not be created")
        else:
            self.signal_status.emit(
                "INFO: Uploaded to https://gfycat.com/{}".format(gfyname))

    def get_upload_status(self, gfyname):
        """Get information about an uploaded GIF. Taken from:
        https://github.com/gfycat/api_clients/blob/master/oauth/url_uploader/python/url_uploader.py
        """
        r = requests.get("{}/{}".format(self.status_endpoint, gfyname))
        if r.status_code != 200:
            self.emit_error("Unable to check the status", r.status_code)
            return None
        res = r.json()
        if "task" not in res:
            self.emit_error("Gfycat API not available")
            return None
        return res["task"]

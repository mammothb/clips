import logging
import os.path
import sys
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
        cwd = os.path.realpath(os.path.dirname(sys.argv[0]))
        with open(os.path.join(cwd, "apikey.txt"), "r") as api_file:
            lines = api_file.readlines()
            self.client_id = lines[0].split("=")[-1].strip()
            self.client_secret = lines[1].split("=")[-1].strip()
            self.username = lines[2].split("=")[-1].strip()
            self.password = lines[3].split("=")[-1].strip()

    def emit_error(self, error_message, status_code=None):
        error = GfycatUploaderError(error_message, status_code)
        LOG.warning(error)
        self.signal_status.emit("ERROR: {}".format(error))

    def get_auth_headers(self):
        body = {
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.username,
            "password": self.password
        }

        r = requests.post(self.token_endpoint, json=body, timeout=3)
        if r.status_code != 200:
            self.emit_error("Error requesting token", r.status_code)
            return None
        auth_headers = {
            "Authorization" : "Bearer {}".format(r.json()["access_token"])
        }
        return auth_headers

    @pyqtSlot(list)
    def upload_from_file(self, file_names):
        """Upload a local file to Gfycat. Taken from:
        https://gist.github.com/hellopatrick/ab6a9dfbbc7c1db7e6b817d06399fffd
        """
        headers = self.get_auth_headers()
        if headers is None:
            return
        for file_name in file_names:
            base_name = os.path.basename(file_name)
            gif_info = {
                "title": os.path.splitext(base_name)[0],
                "noMd5": "true",
                "nsfw": 1
            }
            r = requests.post(self.api_endpoint, json=gif_info,
                              headers=headers)
            if r.status_code != 200:
                self.emit_error("{} - Error requesting ID".format(base_name),
                                r.status_code)
                return
            gfyname = r.json()["gfyname"]
            LOG.info("Requested ID: %s", gfyname)
            with open(file_name, "rb") as source:
                r = requests.put("{}/{}".format(self.filedrop_endpoint,
                                                gfyname), source)
                if r.status_code != 200:
                    self.emit_error("{} - Error uploading file".format(
                        base_name), r.status_code)
                    return
            LOG.info("Encoding %s", base_name)
            status = "encoding"
            wait_count = 0
            while status == "encoding":
                status = self.get_upload_status(gfyname)
                time.sleep(3)
                wait_count += 1
                if wait_count > 300:
                    break
            if status != "complete":
                self.emit_error("{} - Gfycat could not be created".format(
                    base_name))
            else:
                self.signal_status.emit(
                    "INFO: Uploaded to https://gfycat.com/{}".format(
                        gfyname))

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

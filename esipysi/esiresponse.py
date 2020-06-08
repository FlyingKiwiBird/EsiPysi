import json
from datetime import datetime
import pytz
import logging

logger = logging.getLogger("EsiPysi")

class EsiResponse():
    def __init__(self, text, headers, status, url, op_id, op_params):
        self.text = text
        self.headers = headers
        self.status = status
        self.url = url
        self.operation_id = op_id
        self.operation_parameters = op_params

    def json(self):
        try:
            return json.loads(self.text)
        except Exception:
            return None

    def expires(self) -> datetime:
        expires_str = self.headers.get("expires")

        if expires_str is None:
            return None

        try:
            return datetime.strptime(expires_str, "%a, %d %b %Y %H:%M:%S GMT").replace(tzinfo=pytz.utc)
        except:
            logger.warn("Could not parse expires string: '{}'".format(expires_str))
            return None
        


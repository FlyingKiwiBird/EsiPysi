import json
from datetime import datetime
import pytz
import logging

logger = logging.getLogger("EsiPysi")

class EsiResponse():
    """
    A result of an Esi operation, includes information like headers and status code as well as the actual result
    """

    def __init__(self, text, headers, status, url, op_id, op_params):
        self.text = text
        """
        Result in plain text
        """

        self.headers = headers
        """
        Incomming headers in a MultiDict
        """

        self.status = status
        """
        HTTP Status code (200 = OK)
        """

        self.url = url
        """
        The URL that was called
        """

        self.operation_id = op_id
        """
        The function ID which the operation ran on
        """

        self.operation_parameters = op_params
        """
        The parameters that the operation ran on
        """

    def json(self) -> object:
        """
        Parse the text result into a python object representing the JSON object
        """
        try:
            return json.loads(self.text)
        except Exception:
            return None

    def expires(self) -> datetime:
        """
        When this operation expires from the ESI cache
        """
        expires_str = self.headers.get("expires")

        if expires_str is None:
            return None

        try:
            return datetime.strptime(expires_str, "%a, %d %b %Y %H:%M:%S GMT").replace(tzinfo=pytz.utc)
        except:
            logger.warn("Could not parse expires string: '{}'".format(expires_str))
            return None
        


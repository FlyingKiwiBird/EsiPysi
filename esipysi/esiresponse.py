import json

class EsiResponse():
    def __init__(self, text, headers, status, url):
        self.text = text
        self.headers = headers
        self.status = status
        self.url = url

    def json(self):
        try:
            return json.loads(self.text)
        except Exception:
            return None


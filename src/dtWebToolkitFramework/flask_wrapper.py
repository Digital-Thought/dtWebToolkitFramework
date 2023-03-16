from threading import Thread
from flask import Flask, Response


class FlaskAppWrapper(Thread):
    app = None

    def __init__(self, name, settings):
        super().__init__()
        self.settings = settings
        self.app = Flask(name)

    def run(self):
        self.app.run(host=self.settings.get('web_server.host', '127.0.0.1'),
                     port=self.settings.get('web_server.port', 4444), debug=False, threaded=True)

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, methods=None):
        self.app.add_url_rule(endpoint, endpoint_name, handler, methods=methods)

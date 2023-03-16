import os
import flask


class AbstractTool(object):

    def __init__(self, flask_wrapper, app_name, settings):
        super().__init__()
        self.flask_wrapper = flask_wrapper
        self.app_name = app_name
        self.settings = settings
        self.base_resources = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_resources")
        self.add_custom_endpoints()

    def add_custom_endpoints(self):
        raise NotImplementedError

    def name(self):
        raise NotImplementedError

    def short_name(self):
        raise NotImplementedError

    def description(self):
        raise NotImplementedError

    def icon(self):
        raise NotImplementedError

    def tool_home_body_content(self):
        raise NotImplementedError

    def tool_static_content(self, path):
        raise NotImplementedError

    def tool_home(self):
        with open(f'{self.base_resources}/base_template.html', mode='r') as base_template:
            return flask.Response(base_template.read().replace('{{CONTENT}}', self.tool_home_body_content())
                                  .replace('{{APP_NAME}}', self.app_name), 200)

    def error_message(self, friendly, detail):
        with open(f'{self.base_resources}/base_template.html', mode='r') as base_template:
            with open(f'{self.base_resources}/error_card.html', mode='r') as error_card:
                return flask.Response(base_template.read().replace('{{CONTENT}}', error_card.read())
                                      .replace('{{ERROR_FRIENDLY}}', friendly).replace('{{ERROR_DETAILS}}', detail)
                                      .replace('{{APP_NAME}}', self.app_name), 500)

    def please_wait(self, task_id, message):
        with open(f'{self.base_resources}/please_wait_template.html', mode='r') as please_wait_template:
            return flask.Response(please_wait_template.read()
                                  .replace('{{MESSAGE}}', message)
                                  .replace('{{TASK_ID}}', task_id)
                                  .replace('{{APP_NAME}}', self.app_name), 200)

    def add_endpoint(self, endpoint, endpoint_name, handler, methods=None):
        self.flask_wrapper.add_endpoint(endpoint=f'/{self.short_name()}{endpoint}',
                                        endpoint_name=f'{endpoint_name}',
                                        handler=handler, methods=methods)

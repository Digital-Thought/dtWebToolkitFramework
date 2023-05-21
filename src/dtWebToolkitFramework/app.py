import time
from argparse import ArgumentParser
from flask import Flask, flash, request, redirect, render_template_string

from dtAppFramework.app import AbstractApp
from dtAppFramework import settings
from .flask_wrapper import FlaskAppWrapper
from .tool import AbstractTool
from flask import send_from_directory
from threading import Thread

import webbrowser
import logging
import pathlib
import flask
import os
import signal
import importlib


flask_app = None


class AbstractWebToolkit(AbstractApp):

    def __init__(self, description=None, version=None, short_name=None, full_name=None, console_app=True) -> None:
        super().__init__(description=description, version=version, short_name=short_name, full_name=full_name,
                         console_app=console_app)
        self.flask_app = None
        self.tools = []

    def define_args(self, arg_parser: ArgumentParser):
        pass

    def main(self, args):
        self.flask_app = FlaskAppWrapper(self.app_spec['short_name'], settings=self.application_settings)
        self.resource_manager.add_resource_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_resources"))
        self.flask_app.add_endpoint(endpoint='/', endpoint_name='home', handler=self.home)
        self.flask_app.add_endpoint(endpoint='/exit', endpoint_name='exit', handler=self.exit)
        self.flask_app.add_endpoint(endpoint='/assets/<path:path>', endpoint_name='assets', handler=self.assets)

        for util in self.get_utils():
            logging.info(f'Loading Tool: {util}')
            module = importlib.import_module(util)
            tool: AbstractTool = module.Tool(self.flask_app, f"{self.app_spec['full_name']}, Version: {self.app_spec['version']}", self.application_settings)

            if tool.is_enabled():
                self.flask_app.add_endpoint(endpoint=f'/{tool.short_name()}', endpoint_name=tool.short_name(),
                                            handler=tool.tool_home)
            else:
                self.flask_app.add_endpoint(endpoint=f'/{tool.short_name()}', endpoint_name=tool.short_name(),
                                            handler=tool.tool_disabled)

            self.flask_app.add_endpoint(endpoint=f'/{tool.short_name()}/static/<path:path>',
                                        endpoint_name=f'{tool.short_name()}_statics',
                                        handler=tool.tool_static_content)
            self.tools.append(tool)

        self.flask_app.start()

        home_url = f"http://{self.application_settings.get('web_server.host', '127.0.0.1')}:{self.application_settings.get('web_server.port', 4444)}/"
        webbrowser.open(home_url, new=0, autoraise=True)
        logging.info(f'Web Toolkit available on: {home_url}')
        self.flask_app.join()

    def close_app(self):
        time.sleep(2)
        logging.info("Closing app at user's request")
        os._exit(0)

    def exit(self):
        resource_path = self.resource_manager.get_resource_path("exit.html")
        logging.info(f"Rendering: {resource_path}")
        with open(f'{resource_path}', mode='r') as html:
            content = html.read().replace("{{APP_NAME}}", f"{self.app_spec['full_name']}, "
                                                          f"Version: {self.app_spec['version']}")

        thread = Thread(target=self.close_app)
        thread.start()
        return flask.Response(content, 200)

    def home(self):
        resource_path = self.resource_manager.get_resource_path("home.html")
        logging.info(f"Rendering: {resource_path}")
        with open(f'{resource_path}', mode='r') as html:
            content = html.read().replace("{{APP_NAME}}", f"{self.app_spec['full_name']}, "
                                                          f"Version: {self.app_spec['version']}")

            tool_card = []
            for tool in self.tools:
                if tool.is_enabled():
                    card_resource_path = self.resource_manager.get_resource_path("card.html")
                else:
                    card_resource_path = self.resource_manager.get_resource_path("disabled_card.html")
                with open(f'{card_resource_path}', mode='r') as card:
                    card_content = card.read().replace('{{NAME}}', tool.name())\
                        .replace('{{DESCRIPTION}}', tool.description())\
                        .replace('{{ICON}}', tool.icon()) \
                        .replace('{{TOOL_HREF}}', f'/{tool.short_name()}')

                    tool_card.append(card_content)

            card_content = '<div class="row">'
            count = 0
            for card in tool_card:
                card_content = card_content + card
                count += 1

                if count == 3:
                    card_content = card_content + '</div>'
                    count = 0
            card_content = card_content + '</div>'
            content = content.replace('{{CARDS}}', card_content)

            return flask.Response(content, 200)

    def assets(self, path):
        for resource_path in self.resource_manager.resource_paths:
            if os.path.exists(os.path.join(resource_path, "assets", path)):
                logging.info(f"Rendering: {resource_path}/assets/{path}")
                return send_from_directory(f'{resource_path}/assets', path)

    def get_utils(self):
        raise NotImplementedError

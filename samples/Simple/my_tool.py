import sys
import os
import flask
import logging
import traceback
import uuid

from datetime import datetime
from flask import request, jsonify

sys.path.append(os.path.abspath('../../src'))

from dtWebToolkitFramework.tool import AbstractTool

resources = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_resources")


class Tool(AbstractTool):

    def add_custom_endpoints(self):
        self.add_endpoint(endpoint="/submit", endpoint_name="receive_form", handler=self.handle_form, methods=["POST"])
        self.add_endpoint(endpoint="/status", endpoint_name="status", handler=self.status, methods=["GET"])
        self.jobs = {}

    def handle_form(self):
        try:
            request.form.get('week_start')
            id1 = uuid.uuid1()
            self.jobs[str(id1)] = {'started': datetime.now()}
            return self.please_wait(str(id1), 'We are working on it')
        except Exception as ex:
            logging.exception(str(ex))
            return self.error_message(friendly=f'{str(ex)}.<br>Please check you have provided all the required '
                                               f'information and try again.',
                                      detail=traceback.format_exc())

    def status(self):
        print(request)
        entry = {'title': "it is me", 'complete': False}
        entry_date = self.jobs[request.args['task_id']]['started']
        if (datetime.now() - entry_date).seconds > 20:
            entry['title'] = 'Complete'
            entry['complete'] = 'True'
        return jsonify(entry)

    def is_enabled(self):
        return True

    def name(self):
        return "My First Tool"

    def short_name(self):
        return "first_tool"

    def description(self):
        return "This is the first tool I have created for demonstration purposes."

    def icon(self):
        return 'mobi-mbri-responsive-2'

    def disabled_reason(self):
        return "Because I dont feel like enabling it"

    def tool_home_body_content(self):
        with open(f'{resources}/form_upload_body.html', mode='r') as body:
            return body.read()

    def tool_static_content(self, path):
        raise NotImplementedError

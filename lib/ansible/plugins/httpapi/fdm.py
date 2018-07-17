# (c) 2018 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import time
import q

from ansible.module_utils._text import to_text
from ansible.module_utils.network.common.utils import to_list
from ansible.module_utils.connection import ConnectionError
from ansible.module_utils.urls import open_url
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.plugins.httpapi import HttpApiBase

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()

API_PREFIX = "/api/fdm/v2"

class HttpApi(HttpApiBase):
    def send_request(self, data, **message_kwargs):
        pass

    def request_token(self, hostname, username, password):
        self._auth_prefix = '/fdm/token'
        self._auth_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        auth_payload = {
            'grant_type': 'password',
            'username': username,
            'password': password
        }
        url = construct_url(hostname, self._auth_prefix)
        response = open_url(url, method='POST', data=json.dumps(auth_payload),
                headers=self._auth_headers)
        #res = handle_response(response)
        res_text = to_text(response.read())
        res = json.loads(res_text)
        result = handle_auth_response(res)
        q(result)
        return result

    def login(self, username, password):
        self._url = self.connection._url
        self._username = username
        self._password = password
        q(self._url, username, password)
        self._auth = self.request_token(self._url, self._username, self._password)


def construct_url(hostname, path, path_params=None, query_params=None):
    url = hostname + API_PREFIX + path
    if path_params:
        url = url.format(**path_params)
    if query_params:
        url += "?" + urlencode(query_params)
    return url


def handle_auth_response(response):
    if 'error' in response:
        error = response['error']
        raise ConnectionError(error['message'], code=error['code'])

    result = {}
    for key in response:
        if key == 'access_token':
           result['access_token'] = response['access_token']
        if key == 'refresh_token':
           result['refresh_token'] = response['refresh_token']

    return result

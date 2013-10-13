# -*- coding: utf-8 -*-
#
# Copyright 2011, 2013 Mark Lee
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
'''\
Base HTTP Request handler.

.. moduleauthor:: Mark Lee <snakemine@lazymalevolence.com>
'''

import requests


class Request(object):
    '''Handles requests to the Redmine API.'''

    def __init__(self, base_uri, username=None, password=None, api_key=None):
        self._base_uri = base_uri
        self._username = username
        self._password = password
        self._api_key = api_key
        if self._username:
            if self._api_key:
                self.password = 'unused'
            self._auth = (self._username, self._password)
        else:
            self._auth = None

    def _send_request(self, method, path, params={}, data=None):
        uri = '%s%s.%s' % (self._base_uri, path, self._format)
        if self._api_key:
            params['key'] = self._api_key
        return getattr(requests, method)(uri, params=params, data=data,
                                         auth=self._auth)

    def _send(self, method, path, params={}, data=None):
        raise NotImplementedError()

    def get(self, path, params={}):
        return self._send('get', path, params)

    def post(self, path, params={}, data=None):
        return self._send('post', path, params, data)

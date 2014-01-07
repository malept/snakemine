# -*- coding: utf-8 -*-
#
# Copyright 2011, 2013, 2014 Mark Lee
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
from .. import conf


class Request(object):
    '''Handles requests to the Redmine API.'''

    @property
    def _auth(self):
        username = conf.settings.USERNAME
        password = conf.settings.PASSWORD
        api_key = conf.settings.API_KEY
        if username:
            if api_key:
                password = 'unused'
            return (username, password)
        else:
            return None

    def _send_request(self, method, path, params={}, data=None):
        headers = {}
        if method in ('post', 'put'):
            headers['Content-Type'] = self._content_type
        uri = '%s%s.%s' % (conf.settings.BASE_URI, path, self._format)
        api_key = conf.settings.API_KEY
        if api_key:
            params['key'] = api_key
        return getattr(requests, method)(uri, params=params, data=data,
                                         auth=self._auth, headers=headers)

    def _send(self, method, path, params={}, data=None):
        raise NotImplementedError()

    def get(self, path, params={}):
        return self._send('get', path, params)

    def post(self, path, params={}, data=None):
        return self._send('post', path, params, data)

    def put(self, path, params={}, data=None):
        return self._send('put', path, params, data)

    def delete(self, path):
        return self._send('delete', path)

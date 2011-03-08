# -*- coding: utf-8 -*-
'''\
Base HTTP Request handler.

.. moduleauthor:: Mark Lee <snakemine@lazymalevolence.com>
'''

from httplib2 import Http
import urllib


class Request(object):
    '''Handles requests to the Redmine API.'''

    def __init__(self, base_uri, username=None, password=None, api_key=None,
                 cache=None):
        self._base_uri = base_uri
        self._username = username
        self._password = password
        self._api_key = api_key
        self._http = Http(cache=cache)
        if self._username:
            if self._api_key:
                self.password = 'unused'
            print self._username, self._password
            self._http.add_credentials(self._username, self._password)

    def _send_request(self, method, path, params={}, data=None):
        method = method.upper()
        uri = '%s%s.%s' % (self._base_uri, path, self._format)
        if self._api_key:
            params['key'] = self._api_key
        if method == 'GET' and params:
            uri += urllib.urlencode(params)
        elif params and not data:
            data = urllib.urlencode(params)
        return self._http.request(uri, method=method, body=data)

    def _send(self, method, path, params={}, data=None):
        raise NotImplementedError()

    def get(self, path, params={}):
        return self._send('GET', path, params)

    def post(self, path, params={}, data=None):
        return self._send('POST', path, params, data)

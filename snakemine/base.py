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
Base for Redmine models.

.. moduleauthor:: Mark Lee <snakemine@lazymalevolence.com>
'''

# This is XML because the JSON response doesn't send back enough info
# For example, issue author metadata
from .request.xml import Request


class Manager(object):
    '''A Django-like model manager for Redmine resources.'''

    def __init__(self):
        self._request = Request()

    def _get(self, path=None, params={}):
        if not path:
            path = self._path
        return [self._cls(data)
                for data in self._request.get(path, params=params)[1]
                if data]

    def all(self):
        return self._get()

    def filter(self, **kwargs):
        return self._get(params=kwargs)

    def get(self, resource_id):
        return self._get(path='%s/%s' % (self._path, resource_id))[0]


class Resource(object):
    '''A representation of a Redmine resource.'''

    def __init__(self, response):
        self._response = response

    def __getattr__(self, key):
        return getattr(self._response, key)

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.id == other.id

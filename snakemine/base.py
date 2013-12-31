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

from ._compat import items
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

    def _resource_path(self, resource_id):
        return '%s/%s' % (self._path, resource_id)

    def all(self):
        '''
        Retrieves all of the available items for a given resource.

        :rtype: :func:`list` of :class:`Resource`
        '''
        return self._get()

    def filter(self, **kwargs):
        return self._get(params=kwargs)

    def get(self, resource_id):
        '''
        Retrieves a single item for a given resource and ID.

        :param int resource_id: The resource's ID
        :rtype: :class:`Resource`
        '''
        return self._get(self._resource_path(resource_id))[0]

    def _data_to_send(self, data):
        return {
            'object': self._cls.__name__.lower(),
            'data': data,
        }

    def create(self, data):
        '''
        Creates a new :class:`Resource`-derived object.

        :param dict data: The new resource metadata
        :rtype: :class:`Resource`
        '''
        resp = self._request.post(self._path, data=self._data_to_send(data))
        return self._cls(resp[1][0])

    def update(self, resource_id, data):
        self._request.put(self._resource_path(resource_id),
                          data=self._data_to_send(data))

    def delete(self, resource_id):
        self._request.delete(self._resource_path(resource_id))


class Resource(object):
    '''
    An abstract representation of a Redmine resource.

    Much like a Django model, a ``Resource`` typically has a class variable
    named ``objects``, which is an instantiation of the related
    :class:`Manager`.

    :param response: the object the represents the metadata of the
                     resource item
    '''

    def __init__(self, response):
        self._response = response
        self._changed = {}
        self._deleted = False

    def __getattr__(self, key):
        val = self._changed.get(key)
        if val is None:
            if self._response is None:
                return None
            else:
                return getattr(self._response, key)

    def __setattr__(self, key, value):
        if key.startswith('_'):
            super(Resource, self).__setattr__(key, value)
        elif self._deleted:
            raise AttributeError('Resource is deleted')
        else:
            self._changed[key] = value

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.id == other.id

    def save(self):
        '''
        Creates or updates the resource item in Redmine.
        '''
        if self._deleted:
            raise RuntimeError('Resource is deleted')
        elif self._response is None:
            # new object
            resource = self.objects.create(self._changed)
            self._response = resource._response
        else:
            # existing object
            self.objects.update(self.id, self._changed)
            for k, v in items(self._changed):
                setattr(self._response, k, v)
        self._changed = {}

    def delete(self):
        '''Deletes the resource item from Redmine.'''
        if self._response:
            self.objects.delete(self.id)
            self._response = None
            self._deleted = True

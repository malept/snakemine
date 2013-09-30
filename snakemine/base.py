# -*- coding: utf-8 -*-
'''\
Base for Redmine models.

.. moduleauthor:: Mark Lee <snakemine@lazymalevolence.com>
'''

from .request.xml import Request
# TODO Django-like settings handling


class Manager(object):
    '''A Django-like model manager for Redmine resources.'''

    def __init__(self):
        self._request = Request('http://localhost:3000', 'jsmith', 'jsmith')

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

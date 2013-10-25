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


class Response(object):
    def __init__(self, data):
        self._data = data

    def _get_person(self, person):
        return self.person_cls.get(person)


class Person(Response):
    people = {}

    @classmethod
    def get(cls, person):
        pid = person.attrib['id']
        if pid not in cls.people:
            cls.people[pid] = cls(person)
        return cls.people[pid]

    def __repr__(self):
        return '<%s: %s, "%s">' % (self.__class__.__name__, self.id, self.name)


class Comment(object):

    def __repr__(self):
        return '<%s: %d by "%s [%s]">' % \
               (self.__class__.__name__, self.id, self.user.name, self.user.id)

    @property
    def id(self):
        '''
        The Redmine ID of the comment.

        :rtype: int
        '''
        raise NotImplementedError

    @property
    def user(self):
        '''
        The user who made the comment.

        :rtype: Person
        '''
        raise NotImplementedError

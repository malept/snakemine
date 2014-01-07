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

from . import base


class Person(base.Person):
    def __getattr__(self, key):
        return self._data.attrib[key]


class Comment(base.Comment):
    def __init__(self, journal):
        self._journal = journal

    def __getattr__(self, key):
        return getattr(self._journal, key)

    def __str__(self):
        return str(self._journal.notes)

    @property
    def id(self):
        return int(self._journal.attrib['id'])

    @property
    def user(self):
        return Person.get(self._journal.user)


class Response(base.Response):
    person_cls = Person

    def __getattr__(self, key):
        return getattr(self._data, key)

    @property
    def assigned_to(self):
        return self._get_person(self._data.assigned_to)

    @property
    def author(self):
        return self._get_person(self._data.author)

    @property
    def parent_id(self):
        try:
            return self.parent.attrib['id']
        except Exception:
            return None

    @property
    def project_id(self):
        return self.project.attrib['id']

    @property
    def comments(self):
        try:
            return [Comment(x) for x in list(self.journals.journal)]
        except AttributeError:
            return []

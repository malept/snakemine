# -*- coding: utf-8 -*-

from . import base


class Person(base.Person):
    def __init__(self, person):
        self._person = person

    def __getattr__(self, key):
        return self._person.attrib[key]


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


class Response(object):
    def __init__(self, xml):
        self._xml = xml

    def __getattr__(self, key):
        return getattr(self._xml, key)

    def _get_person(self, person):
        return Person.get(person)

    @property
    def assigned_to(self):
        return self._get_person(self._xml.assigned_to)

    @property
    def author(self):
        return self._get_person(self._xml.author)

    @property
    def parent_id(self):
        try:
            return self.parent.attrib['id']
        except Exception:
            return None

    @property
    def project_id(self):
        try:
            return self.project.attrib['id']
        except Exception:
            return None

    @property
    def comments(self):
        try:
            return [Comment(x) for x in list(self.journals.journal)]
        except AttributeError:
            return []

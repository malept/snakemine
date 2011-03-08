# -*- coding: utf-8 -*-


class Comment(object):
    def __init__(self, journal):
        self._journal = journal

    def __getattr__(self, key):
        return getattr(self._journal, key)

    @property
    def id(self):
        return self._journal.attrib['id']


class Person(object):
    people = {}
    def __init__(self, person):
        self._person = person

    def __getattr__(self, key):
        return self._person.attrib[key]

    @classmethod
    def get(cls, person):
        pid = person.attrib['id']
        if pid not in cls.people:
            cls.people[pid] = cls(person)
        return cls.people[pid]

    def __repr__(self):
        return '<%s: %s, "%s">' % (self.__class__.__name__, self.id, self.name)


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

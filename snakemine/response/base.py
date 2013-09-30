# -*- coding: utf-8 -*-


class Person(object):
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

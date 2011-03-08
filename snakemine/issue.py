# -*- coding: utf-8 -*-
'''\
Handling of Redmine issues.

.. moduleauthor:: Mark Lee <snakemine@lazymalevolence.com>
'''

from .base import Manager, Resource
# TODO Django-like settings handling


class IssueManager(Manager):
    '''A Django-like model manager for Redmine issues.'''

    @property
    def _cls(self):
        return Issue

    @property
    def _path(self):
        return '/issues'


class Issue(Resource):
    '''A representation of a Redmine issue.'''

    objects = IssueManager()

    @property
    def parent(self):
        if self.parent_id:
            return self.objects.get(self.parent_id)
        else:
            return None

    @property
    def project(self):
        if self.project_id:
            from .project import Project
            return Project.objects.get(self.project_id)
        else:
            return None

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.id)

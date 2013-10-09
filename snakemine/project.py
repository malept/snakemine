# -*- coding: utf-8 -*-

from .base import Manager, Resource


class ProjectManager(Manager):
    '''A Django-like model manager for Redmine projects.'''

    @property
    def _cls(self):
        return Project

    @property
    def _path(self):
        return '/projects'


class Project(Resource):
    '''A representation of a Redmine project.'''

    objects = ProjectManager()

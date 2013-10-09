# -*- coding: utf-8 -*-

from snakemine.project import Project
from unittest import TestCase


class ProjectTest(TestCase):
    '''Assumes that the Redmine instance with the fixture data is running.'''

    ALL_PROJECT_CT = 6

    def test_all(self):
        projects = Project.objects.all()
        self.assertEqual(self.ALL_PROJECT_CT, len(projects))
        for project in projects:
            self.assertIsInstance(project, Project)

    def test_get(self):
        project = Project.objects.get(1)
        self.assertIsNotNone(project)

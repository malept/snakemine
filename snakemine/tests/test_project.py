# -*- coding: utf-8 -*-
#
# Copyright 2013 Mark Lee
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

from . import TestCase
from snakemine.project import Project


class ProjectTest(TestCase):
    '''Assumes that the Redmine instance with the fixture data is running.'''

    def test_all(self):
        projects = Project.objects.all()
        self.assertIsNotNone(projects)
        self.assertNotEqual(0, len(projects))
        for project in projects:
            self.assertIsInstance(project, Project)

    def test_get(self):
        project = Project.objects.get(1)
        self.assertIsNotNone(project)

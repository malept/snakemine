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
'''\
Handling of `Redmine projects
<http://www.redmine.org/projects/redmine/wiki/Rest_Projects>`_.

.. moduleauthor:: Mark Lee <snakemine@lazymalevolence.com>
'''

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

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
'''\
Handling of `Redmine issues`_.

.. _Redmine issues: http://www.redmine.org/projects/redmine/wiki/Rest_Issues
.. moduleauthor:: Mark Lee <snakemine@lazymalevolence.com>
'''

from .base import Manager, Resource
from .project import Project


class IssueManager(Manager):
    '''A Django-like model manager for Redmine issues.'''

    @property
    def _cls(self):
        return Issue

    @property
    def _path(self):
        return '/issues'

    @property
    def _params(self):
        return {
            'include': 'journals',
        }


class Issue(Resource):
    '''A representation of a Redmine issue.'''

    objects = IssueManager()

    @property
    def parent(self):
        '''
        The parent issue, if specified.

        :rtype: :class:`Issue` or :data:`None`
        '''
        if self.parent_id:
            return self.objects.get(self.parent_id)
        else:
            return None

    @property
    def project(self):
        '''
        The :class:`Project` associated with the issue.
        '''
        # A project relation is required on an Issue, so there is no check to
        # see if ``project_id`` exists.
        return Project.objects.get(self.project_id)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.id)

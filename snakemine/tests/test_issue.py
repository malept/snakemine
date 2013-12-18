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

from snakemine.issue import Issue
from unittest import TestCase


class IssueTest(TestCase):
    '''Assumes that the Redmine instance with the fixture data is running.'''

    def test_all(self):
        issues = Issue.objects.all()
        self.assertIsNotNone(issues)
        self.assertNotEqual(0, len(issues))
        for issue in issues:
            self.assertIsInstance(issue, Issue)

    def test_get(self):
        first_issue = Issue.objects.get(1)
        self.assertIsNotNone(first_issue)

    def test_filter(self):
        issues = Issue.objects.filter(assigned_to_id=2)
        self.assertIsNotNone(issues)
        self.assertNotEqual(len(Issue.objects.all()), len(issues))

    def test_attrs(self):
        issue = Issue.objects.get(1)
        self.assertTrue(hasattr(issue, 'author'))
        self.assertEqual('John Smith', issue.author.name)
        self.assertFalse(hasattr(issue, 'assigned_to'))
        self.assertTrue(hasattr(issue, 'comments'))
        self.assertEqual(2, len(issue.comments))

        issue2 = Issue.objects.get(2)
        self.assertIsNotNone(issue2)
        self.assertTrue(hasattr(issue2, 'assigned_to'))
        self.assertEqual('Dave Lopper', issue2.assigned_to.name)
        self.assertTrue(hasattr(issue2, 'comments'))
        self.assertEqual(1, len(issue2.comments))

    def test_attr_comments(self):
        issue = Issue.objects.get(2)
        self.assertTrue(hasattr(issue, 'comments'))
        self.assertEqual(1, len(issue.comments))
        comment = issue.comments[0]
        self.assertIsInstance(comment.id, int)
        self.assertEqual(comment.notes, str(comment))
        self.assertIsNotNone(comment.user)
        self.assertEqual('John Smith', comment.user.name)

    def test_attr_no_comments(self):
        issue = Issue.objects.get(14)
        self.assertEqual([], issue.comments)

    def test_attr_project(self):
        issue = Issue.objects.get(1)
        project = issue.project
        self.assertIsNotNone(project)

    def test_attr_parent(self):
        child = Issue.objects.get(14)
        parent = child.parent
        self.assertIsNotNone(parent)
        self.assertIsInstance(parent, type(child))
        self.assertIsNone(parent.parent)

    def test_equality(self):
        issue1 = Issue.objects.get(1)
        issue2 = Issue.objects.get(1)
        self.assertNotEqual(id(issue1), id(issue2))
        self.assertEqual(issue1, issue2)

    def test_create_issue(self):
        issue = Issue(None)
        self.assertIsNone(issue.id)
        self.assertIsNone(issue.author)
        issue.project_id = 1
        issue.subject = 'test from unittest'
        issue.save()
        self.assertIsNotNone(issue.id)
        self.assertIsNotNone(issue.author)
        self.assertEqual('John Smith', issue.author.name)

        # make sure we're not sharing anything weird
        issue2 = Issue(None)
        self.assertIsNone(issue2.author)

        # cleanup
        issue.delete()

    def test_update_issue(self):
        issue = Issue(None)
        self.assertIsNone(issue.id)
        issue.project_id = 1
        issue.subject = 'issue to be updated'
        issue.save()
        self.assertIsNotNone(issue.id)
        issue2 = Issue.objects.get(issue.id)
        self.assertEqual(issue, issue2)
        self.assertEqual(issue.subject, issue2.subject)
        updated_subject = 'updated subject'
        issue.subject = updated_subject
        issue.save()
        self.assertNotEqual(issue.subject, issue2.subject)
        issue3 = Issue.objects.get(issue.id)
        self.assertEqual(issue.subject, issue3.subject)

        # cleanup
        issue.delete()

    def test_delete_issue(self):
        issue = Issue(None)
        self.assertIsNone(issue.id)
        issue.project_id = 1
        issue.subject = 'issue to be deleted'
        issue.save()
        self.assertIsNotNone(issue.id)
        issue2 = Issue.objects.get(issue.id)
        self.assertEqual(issue, issue2)
        self.assertEqual(issue.subject, issue2.subject)
        issue.delete()
        with self.assertRaises(AttributeError):
            issue.subject = 'this will fail'
        with self.assertRaises(RuntimeError):
            issue.save()

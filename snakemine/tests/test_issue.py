#!/usr/bin/env python
# -*- coding: utf-8 -*-

from snakemine.issue import Issue
from unittest import TestCase


class IssueTest(TestCase):
    '''Assumes that the Redmine instance with the fixture data is running.'''

    ALL_ISSUE_CT = 11

    def test_all(self):
        issues = Issue.objects.all()
        self.assertEqual(self.ALL_ISSUE_CT, len(issues))
        for issue in issues:
            self.assertIsInstance(issue, Issue)

    def test_get(self):
        first_issue = Issue.objects.get(1)
        self.assertIsNotNone(first_issue)

    def test_filter(self):
        issues = Issue.objects.filter(assigned_to_id=2)
        self.assertIsNotNone(issues)
        self.assertNotEqual(self.ALL_ISSUE_CT, len(issues))

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

    # def test_attr_project(self):
    #     issue = Issue.objects.get(1)
    #     project = issue.project
    #     self.assertIsNotNone(project)

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

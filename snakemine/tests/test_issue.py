#!/usr/bin/env python
# -*- coding: utf-8 -*-

from snakemine.issue import Issue
from unittest import TestCase


class IssueTest(TestCase):

    def test_all(self):
        issues = Issue.objects.all()
        self.assertEqual(10, len(issues))
        for issue in issues:
            self.assertIsInstance(issue, Issue)

    def test_get(self):
        first_issue = Issue.objects.get(1)
        self.assertIsNotNone(first_issue)

    def test_attrs(self):
        issue = Issue.objects.get(1)
        self.assertIsNone(issue.parent)
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

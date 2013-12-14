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

from . import test_environ, test_settings
import logging
from logging.handlers import MemoryHandler
from snakemine.conf import Settings
from snakemine.issue import Issue
from unittest import TestCase


class SettingsTest(TestCase):
    '''Assumes that the Redmine instance with the fixture data is running.'''

    @classmethod
    def setUpClass(cls):
        logger = logging.getLogger('snakemine.conf')
        logger.addHandler(MemoryHandler(100))

    def test_unconfigured(self):
        settings = Settings({})
        with test_environ(SNAKEMINE_SETTINGS_MODULE=None):
            with self.assertRaises(RuntimeError):
                settings.foo

    def test_environ_var_nonexistent_module(self):
        settings = Settings({})
        with test_environ(SNAKEMINE_SETTINGS_MODULE='doesnotexist'):
            with self.assertRaises(RuntimeError):
                settings.foo

    def test_environ_var_valid_module(self):
        settings = Settings({})
        with test_environ(SNAKEMINE_SETTINGS_MODULE='test_settings'):
            self.assertEqual('jsmith', settings.USERNAME)

    def test_environ_var_valid_module_invalid_attr(self):
        settings = Settings({})
        with test_environ(SNAKEMINE_SETTINGS_MODULE='test_settings'):
            with self.assertRaises(AttributeError):
                settings.foo

    def test_double_configure(self):
        settings = Settings({})
        self.assertFalse(settings.configured)
        with test_environ(SNAKEMINE_SETTINGS_MODULE='test_settings'):
            settings.configure()
            self.assertTrue(settings.configured)
            with self.assertRaises(RuntimeError):
                settings.configure()

    def test_configure_with_default_settings(self):
        settings = Settings({})
        defaults = {
            'USERNAME': 'jschmidt',
        }
        with test_environ(SNAKEMINE_SETTINGS_MODULE=None):
            settings.configure(default_settings=defaults)
            self.assertEqual('jschmidt', settings.USERNAME)

    def test_api_key(self):
        with test_settings(USERNAME='jsmith', API_KEY='1234abcd'):
            self.assertIsNotNone(Issue.objects.get(1))

    def test_no_auth(self):
        with test_settings():
            self.assertIsNotNone(Issue.objects.get(1))

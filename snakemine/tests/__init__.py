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

from .. import conf
from contextlib import contextmanager
from copy import deepcopy
import os
import sys
if sys.version_info < (2, 7):  # pragma: no cover
    from unittest2 import TestCase as BaseTestCase
else:  # pragma: no cover
    from unittest import TestCase as BaseTestCase

__all__ = ['test_environ', 'test_settings', 'TestCase']


class TestCase(BaseTestCase):
    def setUp(self):
        os.environ['SNAKEMINE_SETTINGS_MODULE'] = 'test_settings'
        conf.settings = conf.Settings(conf.DEFAULT_SETTINGS)


@contextmanager
def test_environ(**kwargs):
    '''
    Allows a test to use a custom :data:`os.environ`. If a key is set to
    :data:`None`, the environment variable is unset for the duration
    of the test.
    '''
    old_environ = deepcopy(os.environ)
    for k, v in kwargs.iteritems():
        if k in os.environ and v is None:
            del os.environ[k]
        else:
            os.environ[k] = v
    yield
    os.environ = old_environ


@contextmanager
def test_settings(**kwargs):
    '''
    Allows a test to use a custom set of settings, which essentially means that
    it replaces :data:`snakemine.conf.settings` for the duration
    of the context.
    '''
    settings = conf.Settings(conf.DEFAULT_SETTINGS)
    settings.configure(**kwargs)
    old_settings = conf.settings
    conf.settings = settings
    yield
    conf.settings = old_settings

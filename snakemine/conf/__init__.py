# -*- coding: utf-8 -*-
#
# Copyright 2013, 2014 Mark Lee
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
A settings manager inspired by Django's.

There are two ways to set user-specific settings:

1. Create a module with all of the settings in it and point snakemine to the
   module via the ``SNAKEMINE_SETTINGS_MODULE`` environment variable.
2. Use :func:`Settings.configure` to set the values via its
   keyword arguments.

.. moduleauthor:: Mark Lee <snakemine@lazymalevolence.com>
'''

from .._compat import items
from .global_settings import DEFAULT_SETTINGS
from copy import deepcopy
from importlib import import_module
import logging
import os

logger = logging.getLogger(__name__)


class Settings(object):
    '''
    Settings object for :mod:`snakemine`.

    :param dict default_settings: The default settings. A copy of this
                                  parameter is stored in the created object.
    '''

    def __init__(self, default_settings):
        self._defaults = deepcopy(default_settings)
        self._user_settings = {}
        self._configured = False

    def configure(self, default_settings=None, **kwargs):
        '''
        Manually configures the user settings instead of via the import module
        method. This method can only be called if the object has not already
        had user settings set.

        :param dict default_settings: The default settings, which will
                                      override the default settings passed in
                                      at object creation.
        '''
        if self.configured:
            msg = 'Settings for snakemine have already been configured'
            raise RuntimeError(msg)
        if default_settings:
            self._defaults = default_settings
        self._set_from_kwargs(**kwargs)
        self._configured = True

    @property
    def configured(self):
        '''
        Whether the user settings have been set for the object.

        :rtype: :func:`bool`
        '''
        return self._configured

    def __getattr__(self, attr):
        if not self.configured:
            # lazily import the module
            self._set_from_environ_var()
            if not self.configured:
                msg = 'Settings for snakemine have not been configured'
                raise RuntimeError(msg)
        try:
            try:
                return self._user_settings[attr]
            except KeyError:
                return self._defaults[attr]
        except KeyError:
            raise AttributeError(attr)

    def _set_from_environ_var(self):
        module_name = os.environ.get('SNAKEMINE_SETTINGS_MODULE', 'settings')
        try:
            module = import_module(module_name)
            self._set_from_module(module)
            self._configured = True
        except ImportError:
            msg = 'Could not find settings file: {0}'.format(module_name)
            logger.warn(msg)

    def _set_from_kwargs(self, **kwargs):
        self._user_settings.update(kwargs)

    def _set_from_module(self, module):
        for k, v in items(vars(module)):
            if k.upper() == k:
                self._user_settings[k] = v

settings = Settings(DEFAULT_SETTINGS)

# -*- coding: utf-8 -*-

import os

BASE_URI = 'http://127.0.0.1:{0}'.format(os.environ.get('REDMINE_PORT',
                                                        '3000'))
USERNAME = 'jsmith'
PASSWORD = 'jsmith'

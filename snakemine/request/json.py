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
HTTP Request handler using the JSON version of the API.

.. moduleauthor:: Mark Lee <snakemine@lazymalevolence.com>
'''

from __future__ import absolute_import

from . import base
from ..response.json import Response
from datetime import date, datetime
from dateutil.parser import parse
from decimal import Decimal
try:
    import simplejson as json
except ImportError:
    import json

DATE_FIELDS = [
    'due_date',
    'start_date',
]
DATETIME_FIELDS = [
    'created_on',
    'updated_on',
]

DATE_FORMAT = '%Y/%m/%d'
DATETIME_FORMAT = '%Y/%m/%d %H:%M:%S %z'


class JSONEncoder(json.JSONEncoder):
    '''Encodes :class:`datetime.date` and :class:`datetime.datetime` objects
    into JSON.
    '''

    def default(self, obj):
        if isinstance(obj, date):
            return obj.strftime(DATE_FORMAT)
        elif isinstance(obj, datetime):
            return obj.strftime(DATETIME_FORMAT)
        return super(JSONEncoder, self).default(obj)


def deserialize_json(dct):
    for field in DATE_FIELDS:
        if field in dct and dct[field]:
            dct[field] = datetime.strptime(dct[field], DATE_FORMAT).date()
    for field in DATETIME_FIELDS:
        if field in dct and dct[field]:
            dct[field] = parse(dct[field])
    return dct


class Request(base.Request):
    '''Handles requests to the Redmine API using JSON.'''
    _format = 'json'
    _content_type = 'application/json'

    def _send(self, method, path, params={}, data=None):
        response = self._send_request(method, path, params=params, data=data)
        result = None
        if response.status_code == 200:
            result = json.loads(response.text, object_hook=deserialize_json,
                                parse_float=Decimal)
        if isinstance(result, list):
            result = [Response(r) for r in result]
        else:
            result = [Response(result)]
        return response.status_code, result

    def post_object(self, path, data):
        return self.post(path, data=json.dumps(data, cls=JSONEncoder))

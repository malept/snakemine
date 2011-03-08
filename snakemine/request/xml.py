# -*- coding: utf-8 -*-
'''\
HTTP Request handler using the JSON version of the API.

.. moduleauthor:: Mark Lee <snakemine@lazymalevolence.com>
'''

from . import base
from ..response.xml import Response
from lxml import objectify

#TODO see http://codespeak.net/svn/lxml/trunk/doc/s5/ep2008/atom.py for pointers on element class lookup and custom element classes


class Date():
    pass


class DateTime():
    pass


class Request(base.Request):
    '''Handles requests to the Redmine API using XML.'''
    _format = 'xml'

    def _send(self, method, path, params={}, data=None):
        response, content = self._send_request(method, path, params=params,
                                               data=data)
        result = None
        if response['status'] == '200':
            xml = objectify.fromstring(content)
            #print objectify.dump(xml)
            result = []
            if xml.tag == 'issues':
                for issue in list(xml.issue):
                    result.append(Response(issue))
            elif xml.tag == 'issue':
                result.append(Response(xml))
            #print etree.tostring(xml, pretty_print=True)
        return response['status'], result

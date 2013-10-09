# -*- coding: utf-8 -*-
'''\
HTTP Request handler using the JSON version of the API.

.. moduleauthor:: Mark Lee <snakemine@lazymalevolence.com>
'''

from . import base
from ..response.xml import Response
from lxml import objectify

# TODO see http://codespeak.net/svn/lxml/trunk/doc/s5/ep2008/atom.py for
# TODO pointers on element class lookup and custom element classes


class Date():
    pass


class DateTime():
    pass


class Request(base.Request):
    '''Handles requests to the Redmine API using XML.'''
    _format = 'xml'

    def _send(self, method, path, params={}, data=None):
        response = self._send_request(method, path, params=params, data=data)
        result = None
        if response.status_code == 200:
            xml = objectify.fromstring(response.text.encode('utf-8'))
            #print objectify.dump(xml)
            result = []
            if xml.tag == 'issues':
                for issue in list(xml.issue):
                    result.append(Response(issue))
            elif xml.tag == 'issue':
                result.append(Response(xml))
            elif xml.tag == 'projects':
                for project in list(xml.project):
                    result.append(Response(project))
            elif xml.tag == 'project':
                result.append(Response(xml))
            #print etree.tostring(xml, pretty_print=True)
        return response.status_code, result

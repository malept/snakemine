Snakemine: A Pythonic interface to Redmine's REST API
=====================================================

This library is a REST API wrapper for the Redmine_ project management web
application. Its API is directly inspired by Django's settings module and ORM.

.. _Redmine: http://www.redmine.org/

Installation
------------

Install-time requirements:

* CPython 2.6 / 2.7 / 3.3 or PyPy (although PyPy is not currently tested on
  Travis CI due to a strange bug, it is tested regularly via tox)
* If you're using Python 2.6:

  * argparse_
  * importlib_

* lxml_
* python-dateutil_
* requests_

.. _argparse: https://pypi.python.org/pypi/argparse
.. _importlib: https://pypi.python.org/pypi/importlib
.. _lxml: http://lxml.de/
.. _python-dateutil: http://labix.org/python-dateutil
.. _requests: http://python-requests.org/

Run-time requirements:

* A Redmine_ installation somewhere (this has only been tested with 1.0, I
  make no guarantees at this point that it works with any newer version)

Example
-------

Let's assume that you have a registered user with an API key.

Here is the Django-esque settings file (named ``redmine_settings.py``):

.. code-block:: python

   BASE_URI = 'https://redmine.example.com'
   USERNAME = 'jschmidt'
   API_KEY = '1234abcd'

Here is a way to retrieve a given issue and change its subject (creatively
named ``script.py``):

.. code-block:: python

   from snakemine.issue import Issue

   issue = Issue.objects.get(12)
   issue.subject = 'Modified subject'
   issue.save()

You would run the script like so:

.. code-block:: sh

   PYTHONPATH=. SNAKEMINE_SETTINGS_MODULE=redmine_settings python script.py

License
-------

Apache License 2.0; see the ``LICENSE`` file for details.

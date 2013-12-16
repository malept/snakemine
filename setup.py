#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import find_packages, setup
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from snakemine import metadata

with open('README.rst') as f:
    long_description = f.read()

requires = []
if not os.environ.get('READTHEDOCS'):
    requires = [l for l in open('requirements.txt')]

setup(name='snakemine',
      version=metadata.VERSION,
      description=metadata.DESCRIPTION,
      long_description=long_description,
      author='Mark Lee',
      author_email='snakemine@lazymalevolence.com',
      url='https://snakemine.readthedocs.org/',
      packages=find_packages(),
      install_requires=requires,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: Implementation :: CPython',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ])

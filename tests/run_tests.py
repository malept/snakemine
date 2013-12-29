#!/usr/bin/env python
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

from __future__ import print_function

from contextlib import contextmanager
from functools import partial
import os
import re
import requests
from shutil import copy, rmtree
from signal import SIGKILL
from subprocess import PIPE, Popen
import sys
from tempfile import NamedTemporaryFile
import time

try:
    from coverage import coverage
except ImportError:
    coverage = None

try:
    import unittest2 as unittest
except ImportError:
    import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(TEST_DIR)
DEFAULT_RM_VERSION = '1.0.4'

# ENVIRONMENT
DOWNLOAD_CACHE = os.environ.get('DOWNLOAD_CACHE', '/tmp')
UNZIP_DIR = os.environ.get('UNZIP_DIR', '/tmp')
RM_DOWNLOAD_METHOD = os.environ.get('REDMINE_DOWNLOAD_METHOD', 'TGZ')
RM_VERSION = os.environ.get('REDMINE_VERSION', DEFAULT_RM_VERSION)
RVM_NOT_SET = os.environ.get('RVM_ALREADY_SET') is None
RM_SETUP_NEEDED = os.environ.get('NO_SETUP_NEEDED') is None
RM_PORT = os.environ.get('REDMINE_PORT', '3000')
RUN_COVERAGE = os.environ.get('RUN_COVERAGE')

# REDMINE DATA
RM_VERSION_INFO = tuple(RM_VERSION.split('.'))
RM_DIRNAME = 'redmine-{0}'.format(RM_VERSION)
RM_TGZ = '{0}.tar.gz'.format(RM_DIRNAME)
RM_TGZ_URL = \
    'http://files.rubyforge.vm.bytemark.co.uk/redmine/{0}'.format(RM_TGZ)
RM_SVN_URL = 'http://svn.redmine.org/redmine/tags/{0}'.format(RM_VERSION)
LOCAL_RM_TGZ = os.path.join(DOWNLOAD_CACHE, RM_TGZ)
LOCAL_RM_DIR = os.path.join(UNZIP_DIR, RM_DIRNAME)

RAILS_ENV = os.environ.copy()
RAILS_ENV['RAILS_ENV'] = 'production'

RM_DEPS_1_0 = {
    'rack': '1.0.1',
    'rails': '2.3.5',
    'ruby': '1.8.7',
    'rubygems': '1.4.2',
}
RM_DEPS_1_0_5 = RM_DEPS_1_0.copy()
RM_DEPS_1_0_5['i18n'] = '0.4.2'

RM_DEPS = {
    '1.0.1': RM_DEPS_1_0,
    '1.0.2': RM_DEPS_1_0,
    '1.0.3': RM_DEPS_1_0,
    '1.0.4': RM_DEPS_1_0,
    '1.0.5': RM_DEPS_1_0_5,
}

# Functions


def run(*cmd, **kwargs):
    stdin = kwargs.pop('stdin', None)
    kwargs['stdin'] = PIPE
    proc = Popen(cmd, **kwargs)
    stdout, stderr = proc.communicate(stdin)
    if proc.returncode != 0:
        msg = 'Failure when running: {0}\n'.format(' '.join(cmd))
        sys.stderr.write(msg)
        sys.exit(proc.returncode)
    if kwargs.get('stdout') == PIPE:
        return stdout
    else:
        return proc.pid


def rvm(*args, **kwargs):
    cmd = 'rvm {0}'.format(' '.join(args))
    kwargs['shell'] = True
    return run(cmd, **kwargs)

ruby_version = RM_DEPS[RM_VERSION]['ruby']
rvm_do = partial(rvm, ruby_version, 'do')

gem = partial(rvm_do, 'gem')


def gem_unpack(name, version, unpack_dir):
    gem_id = '{0}-{1}'.format(name, version)
    gem_file = '{0}.gem'.format(gem_id)
    local_gem = os.path.join(DOWNLOAD_CACHE, gem_file)
    if not os.path.exists(local_gem):
        print('Downloading the {0} gem...'.format(gem_id))
        gem('fetch', name, '-v', version, cwd=DOWNLOAD_CACHE)
    gem('unpack', local_gem, cwd=unpack_dir)


def gem_install(*gem_args, **kwargs):
    cmd = ['install', '--no-ri', '--no-rdoc'] + list(gem_args)
    return gem(*cmd, **kwargs)

run_with_rails = partial(rvm_do, env=RAILS_ENV)


@contextmanager
def remove_installed_global_gems():
    global_gems_filename = os.path.expanduser('~/.rvm/gemsets/global.gems')
    open_global_gems = partial(open, global_gems_filename)
    write_global_gems = partial(open_global_gems, 'w')
    with open_global_gems() as f:
        global_gems = f.read()
    with write_global_gems() as f:
        f.write('\n'.join([l for l in global_gems.split('\n')
                           if 'bundler' not in l and 'rake' not in l]))
    yield
    with write_global_gems() as f:
        f.write(global_gems)


def replace_in_file(search, replace, filename):
    with open(filename) as f:
        data = f.read()

    data = re.sub(search, replace, data)

    with open(filename, 'w') as f:
        f.write(data)


@contextmanager
def code_coverage():
    if RUN_COVERAGE and coverage:
        print("Code coverage enabled.")
        cov = coverage(config_file=os.path.join(BASE_DIR, '.coveragerc'))
        cov.start()

    yield

    if RUN_COVERAGE and coverage:
        cov.stop()
        cov.report()

# Logic

run('flake8', '--exclude=.tox', BASE_DIR)

if RVM_NOT_SET:
    # Set the correct RVM ruby (1.8.7) if RVM is installed
    installed_rubies = rvm('list', 'strings', stdout=PIPE)
    if ruby_version in installed_rubies:
        print('Using Ruby {0}...'.format(ruby_version))
    else:
        print('Installing Ruby {0}...'.format(ruby_version))
        with remove_installed_global_gems():
            rvm('install', ruby_version)
            rvm_do('rvm', 'rubygems', RM_DEPS[RM_VERSION]['rubygems'])

if RM_SETUP_NEEDED:
    if os.path.isdir(LOCAL_RM_DIR):
        print('Re-creating Redmine install...')
        rmtree(LOCAL_RM_DIR)

    if RM_DOWNLOAD_METHOD == 'SVN':
        run('svn', 'co', RM_SVN_URL, LOCAL_RM_DIR)
    else:
        if not os.path.exists(LOCAL_RM_TGZ):
            print('Downloading Redmine {0}...'.format(RM_VERSION))
            run('wget', '-O', LOCAL_RM_TGZ, RM_TGZ_URL)
        run('tar', '-C', UNZIP_DIR, '-xf', LOCAL_RM_TGZ)
    if 'sqlite3' not in gem('list', stdout=PIPE):
        gem_install('sqlite3')

    os.chdir(LOCAL_RM_DIR)
    # enable the REST API
    replace_in_file(r'(rest_api_enabled:\s+default:) 0', r'\1 1',
                    os.path.join(LOCAL_RM_DIR, 'config/settings.yml'))
    copy(os.path.join(TEST_DIR, 'database.yml'),
         os.path.join(LOCAL_RM_DIR, 'config'))

    if RM_DOWNLOAD_METHOD == 'SVN':
        # if redmine comes from SVN, install rails too
        gem_install('rake', '-v', '0.8.7')
        gem_install('rails', '-v', RM_DEPS[RM_VERSION]['rails'])
        gem_install('rdoc')
        replace_in_file('rake/rdoctask', 'rdoc/task',
                        os.path.join(LOCAL_RM_DIR, 'Rakefile'))
    else:
        gem_unpack('rack', RM_DEPS[RM_VERSION]['rack'],
                   os.path.join(LOCAL_RM_DIR, 'vendor/gems'))
    if 'i18n' in RM_DEPS[RM_VERSION]:
        gem_install('i18n', '-v', '0.4.2')

    prod_rb = os.path.join(LOCAL_RM_DIR, 'config/environments/production.rb')
    session_data = '''
config.action_controller.session = {
  :key => "_redmine_session",
  :secret => "31ea0a98608815189ee8118e6d6bbcbb",
}'''
    with open(prod_rb, 'a') as f:
        f.write(session_data)

    run_with_rails('rake', 'generate_session_store', 'db:migrate',
                   'db:fixtures:load')
    test_data = '''
Token.create!(:action => "api", :user_id => 2, :value => "1234abcd")
Issue.create!(:parent_issue_id => 1, :subject => "parent issue test",
              :tracker_id => 1, :project_id => 1,
              :description => "Parent issue test", :author_id => 3)
'''
    with NamedTemporaryFile() as f:
        f.write(test_data)
        f.flush()
        run_with_rails('script/runner', f.name)
else:
    os.chdir(LOCAL_RM_DIR)

pid = run_with_rails('script/server', '--daemon', '--binding=127.0.0.1',
                     '--port={0}'.format(RM_PORT))
# make sure the stupid server is ready to accept connections before
# running tests
print('Waiting for Redmine to be responsive...')
redmine_responsive = False
while not redmine_responsive:
    try:
        r = requests.head('http://127.0.0.1:{0}'.format(RM_PORT))
        if r.status_code == 200:
            redmine_responsive = True
    except Exception:
        pass
    print('.', end='')
    time.sleep(1)
print()

print()
print('Starting tests...')
print()

sys.path.append(TEST_DIR)
os.environ['SNAKEMINE_SETTINGS_MODULE'] = 'test_settings'

os.chdir(BASE_DIR)
with code_coverage():
    test_suite = unittest.defaultTestLoader.discover(BASE_DIR)
    runner = unittest.TextTestRunner()
    runner.run(test_suite)

pidfile = os.path.join(LOCAL_RM_DIR, 'tmp/pids/server.pid')
if os.path.exists(pidfile):
    pid = int(open(pidfile).read().strip())
    os.remove(pidfile)

os.kill(pid, SIGKILL)

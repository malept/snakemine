#!/usr/bin/env python
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

from __future__ import print_function

import argparse
try:
    import argcomplete
except ImportError:
    argcomplete = None
from contextlib import contextmanager
from flake8.engine import get_style_guide
from flake8.main import print_report
from functools import partial
import os
from random import randint
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
DEFAULT_PORT = 3000
RAND_PORT_MIN = 3000
RAND_PORT_MAX = 65535

# REDMINE DATA
RM_TGZ_FMT = 'http://files.rubyforge.vm.bytemark.co.uk/redmine/{0}'

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
    '1.1.0': RM_DEPS_1_0_5,
    '1.1.1': RM_DEPS_1_0_5,
    '1.1.2': RM_DEPS_1_0_5,
    '1.1.3': RM_DEPS_1_0_5,
}

# Functions


def parse_args(prog, args):
    parser = argparse.ArgumentParser(prog)
    parser.add_argument('--redmine-version', default=DEFAULT_RM_VERSION,
                        metavar='VERSION',
                        help='The version of Redmine to test against')
    parser.add_argument('--use-existing-redmine-install', action='store_false',
                        default=True, dest='redmine_setup_needed',
                        help='Use the existing Redmine install instead of '
                             'recreating it')
    parser.add_argument('--redmine-download-method', default='TGZ',
                        choices=['TGZ', 'SVN'],
                        help='The method that the Redmine code is downloaded')
    parser.add_argument('--redmine-port', type=int, default=DEFAULT_PORT,
                        help='The TCP port Redmine will listen on')
    parser.add_argument('--redmine-port-random', action='store_true',
                        default=False,
                        help='Randomly sets the Redmine TCP port '
                             '(overrides --redmine-port)')
    parser.add_argument('--no-flake8', action='store_false', default=True,
                        dest='flake8', help='Disable Flake8 check')
    parser.add_argument('--check-rvm-ruby', action='store_true', default=False,
                        help='Installs the proper RVM Ruby version if not '
                             'already installed')
    parser.add_argument('--workspace', metavar='DIR', default='/tmp',
                        help='Directory where Redmine directory is located')
    parser.add_argument('--download-cache', metavar='DIR', default='/tmp',
                        help='Directory where tarballs/gems are cached')
    parser.add_argument('--run-coverage', action='store_true', default=False,
                        help='Run coverage.py on the testsuite')

    if argcomplete:
        argcomplete.autocomplete(parser)
    return parser.parse_args(args)


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
        return str(stdout)
    else:
        return proc.pid


def svn_checkout(redmine_version, target_dir):
    url = 'http://svn.redmine.org/redmine/tags/{0}'.format(redmine_version)
    run('svn', 'co', url, target_dir)


def unpack_tarball(args, redmine_dirname):
    tgz_basename = '{0}.tar.gz'.format(redmine_dirname)
    tgz_url = RM_TGZ_FMT.format(tgz_basename)
    tgz_path = os.path.join(args.download_cache, tgz_basename)
    if not os.path.exists(tgz_path):
        print('Downloading Redmine {0}...'.format(args.redmine_version))
        run('wget', '-O', tgz_path, tgz_url)
    run('tar', '-C', args.workspace, '-xf', tgz_path)


class RVM(object):
    def __init__(self, ruby_version, download_cache):
        self.download_cache = download_cache
        self.ruby_version = ruby_version
        self.do = partial(self, self.ruby_version, 'do')

        self.gem = partial(self.do, 'gem')
        self.gem_list = partial(self.gem, 'list', stdout=PIPE)
        self.with_rails = partial(self.do, env=RAILS_ENV)

    def __call__(self, *args, **kwargs):
        cmd = 'rvm {0}'.format(' '.join(args))
        kwargs['shell'] = True
        return run(cmd, **kwargs)

    def gem_unpack(self, name, version, unpack_dir):
        gem_id = '{0}-{1}'.format(name, version)
        gem_file = '{0}.gem'.format(gem_id)
        local_gem = os.path.join(self.download_cache, gem_file)
        if not os.path.exists(local_gem):
            print('Downloading the {0} gem...'.format(gem_id))
            self.gem('fetch', name, '-v', version, cwd=self.download_cache)
        self.gem('unpack', local_gem, cwd=unpack_dir)

    def gem_install(self, *gem_args, **kwargs):
        cmd = ['install', '--no-ri', '--no-rdoc'] + list(gem_args)
        return self.gem(*cmd, **kwargs)

    def check_and_install(self, rubygems_version):
        '''Install the correct RVM ruby and rubygems versions.'''
        installed_rubies = self('list', 'strings', stdout=PIPE)
        if self.ruby_version in installed_rubies:
            print('Using Ruby {0}...'.format(self.ruby_version))
        else:
            print('Installing Ruby {0}...'.format(self.ruby_version))
            with remove_installed_global_gems():
                self('install', self.ruby_version)
                self.do('rvm', 'rubygems', rubygems_version)


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
def code_coverage(args):
    if args.run_coverage and coverage:
        print("Code coverage enabled.")
        cov = coverage(config_file=os.path.join(BASE_DIR, '.coveragerc'))
        cov.start()

    yield

    if args.run_coverage and coverage:
        cov.stop()
        cov.report()


def run_flake8():
    flake8 = get_style_guide(exclude=['.tox', 'build'])
    report = flake8.check_files([BASE_DIR])

    return print_report(report, flake8)


def main(argv):
    args = parse_args(argv[0], argv[1:])

    if args.redmine_port_random:
        redmine_port = randint(RAND_PORT_MIN, RAND_PORT_MAX)
    else:
        redmine_port = args.redmine_port

    dep_versions = RM_DEPS[args.redmine_version]
    rvm = RVM(dep_versions['ruby'], args.download_cache)

    redmine_dirname = 'redmine-{0}'.format(args.redmine_version)
    local_redmine_dir = os.path.join(args.workspace, redmine_dirname)

    if args.flake8:
        exit_code = run_flake8()
        if exit_code > 0:
            return exit_code

    if args.check_rvm_ruby:
        rvm.check_and_install(dep_versions['rubygems'])

    if args.redmine_setup_needed:
        if os.path.isdir(local_redmine_dir):
            print('Re-creating Redmine install...')
            rmtree(local_redmine_dir)

        if args.redmine_download_method == 'SVN':
            svn_checkout(args.redmine_version, local_redmine_dir)
        else:
            unpack_tarball(args, redmine_dirname)
        if 'sqlite3' not in rvm.gem_list():
            rvm.gem_install('sqlite3')

        os.chdir(local_redmine_dir)
        # Enable the REST API via the settings YAML file.
        replace_in_file(r'(rest_api_enabled:\s+default:) 0', r'\1 1',
                        os.path.join(local_redmine_dir, 'config/settings.yml'))
        copy(os.path.join(TEST_DIR, 'database.yml'),
             os.path.join(local_redmine_dir, 'config'))

        if args.redmine_download_method == 'SVN':
            # If Redmine comes from SVN, install Rails too.
            rvm.gem_install('rails', '-v', dep_versions['rails'])
            rvm.gem('list')
        else:
            rvm.gem_unpack('rack', dep_versions['rack'],
                           os.path.join(local_redmine_dir, 'vendor/gems'))
        if 'rake' in rvm.gem_list():
            rvm.gem('uninstall', '-a', '-x', 'rake')
        rvm.gem_install('rake', '-v', '0.8.7')
        replace_in_file('rake/rdoctask', 'rdoc/task',
                        os.path.join(local_redmine_dir, 'Rakefile'))
        rvm.gem_install('rdoc')
        if 'i18n' in dep_versions:
            rvm.gem_install('i18n', '-v', dep_versions['i18n'])

        prod_rb = os.path.join(local_redmine_dir,
                               'config/environments/production.rb')
        # TODO convert into append_to_file
        session_data = '''
config.action_controller.session = {
  :key => "_redmine_session",
  :secret => "31ea0a98608815189ee8118e6d6bbcbb",
}'''
        with open(prod_rb, 'a') as f:
            f.write(session_data)

        rvm.with_rails('rake', 'generate_session_store', 'db:migrate',
                       'db:fixtures:load')
        test_data = b'''
Token.create!(:action => "api", :user_id => 2, :value => "1234abcd")
Issue.create!(:parent_issue_id => 1, :subject => "parent issue test",
              :tracker_id => 1, :project_id => 1,
              :description => "Parent issue test", :author_id => 3)
'''
        with NamedTemporaryFile() as f:
            f.write(test_data)
            f.flush()
            rvm.with_rails('script/runner', f.name)
    else:
        os.chdir(local_redmine_dir)

    # TODO convert into contextmanager
    pid = rvm.with_rails('script/server', '--daemon', '--binding=127.0.0.1',
                         '--port={0}'.format(redmine_port))
    # make sure the stupid server is ready to accept connections before
    # running tests
    print('Waiting for Redmine to be responsive...')
    redmine_responsive = False
    while not redmine_responsive:
        try:
            r = requests.head('http://127.0.0.1:{0}'.format(redmine_port))
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
    if 'REDMINE_PORT' not in os.environ:
        os.environ['REDMINE_PORT'] = str(redmine_port)

    os.chdir(BASE_DIR)
    with code_coverage(args):
        test_suite = unittest.defaultTestLoader.discover(BASE_DIR)
        runner = unittest.TextTestRunner()
        result = runner.run(test_suite)

    pidfile = os.path.join(local_redmine_dir, 'tmp/pids/server.pid')
    if os.path.exists(pidfile):
        pid = int(open(pidfile).read().strip())
        os.remove(pidfile)

    # TODO convert into contextmanager
    os.kill(pid, SIGKILL)

    if not result.wasSuccessful():
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))

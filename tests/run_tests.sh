#!/bin/bash
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

BASE_DIR="$(pwd)/$(dirname $0)"

[[ -z "$DOWNLOAD_CACHE" ]] && DOWNLOAD_CACHE=/tmp

[[ -z "$UNZIP_DIR" ]] && UNZIP_DIR=/tmp

REDMINE_VERSION=1.0.4
REDMINE_DIR=redmine-${REDMINE_VERSION}
REDMINE_TGZ=${REDMINE_DIR}.tar.gz
REDMINE_TGZ_URL=http://rubyforge.org/frs/download.php/73457/${REDMINE_TGZ}

LOCAL_REDMINE_TGZ="$DOWNLOAD_CACHE/$REDMINE_TGZ"
LOCAL_REDMINE_DIR="$UNZIP_DIR/$REDMINE_DIR"

flake8 . || exit 1

if [[ -z "$NO_SETUP_NEEDED" ]]; then
    if [[ ! -f "$LOCAL_REDMINE_TGZ" ]]; then
        echo "Downloading Redmine ${REDMINE_VERSION} from the internet..."
        wget -O "$LOCAL_REDMINE_TGZ" "$REDMINE_TGZ_URL"
    fi

    if [[ -d "$LOCAL_REDMINE_DIR" ]]; then
        echo 'Re-creating Redmine install...'
        rm -r "$LOCAL_REDMINE_DIR"
    fi

    tar -C "$UNZIP_DIR" -xf "$LOCAL_REDMINE_TGZ"
    cd "$LOCAL_REDMINE_DIR"
    perl -0 -i -pe 's@(rest_api_enabled:\s+default:) 0@$1 1@msg' config/settings.yml
    cp "$BASE_DIR"/database.yml "$LOCAL_REDMINE_DIR"/config/
    # install one gem locally
    (
        cd vendor/gems
        gem fetch rack -v '~> 1.0.1'
        gem unpack rack-1.0.1.gem
        rm rack-1.0.1.gem
    )
    RAILS_ENV=production rake generate_session_store db:migrate db:fixtures:load
    RAILS_ENV=production script/runner 'Token.create!(:action => "api", :user_id => 2, :value => "1234abcd");
Issue.create!(:parent_issue_id => 1, :subject => "parent issue test", :tracker_id => 1, :project_id => 1, :description => "Parent issue test", :author_id => 3)'
else
    cd "$LOCAL_REDMINE_DIR"
fi

RAILS_ENV=production script/server --daemon --binding=127.0.0.1
# make sure the stupid server is ready to accept connections before running tests
echo 'Waiting for Redmine to be responsive...'
while [[ $(curl -q http://127.0.0.1:3000 2> /dev/null > /dev/null; echo $?) != 0 ]]; do
    echo -n .
    sleep 1
done

echo
echo 'Starting tests...'
echo

(
    cd "$BASE_DIR"/..
    PYTHONPATH="$BASE_DIR" SNAKEMINE_SETTINGS_MODULE="test_settings" coverage run -m unittest discover
    coverage report -m
)
kill -9 `cat tmp/pids/server.pid`

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

[[ -z "$REDMINE_DOWNLOAD_METHOD" ]] && REDMINE_DOWNLOAD_METHOD=TGZ

REDMINE_VERSION=1.0.4
REDMINE_DIR=redmine-${REDMINE_VERSION}
REDMINE_TGZ=${REDMINE_DIR}.tar.gz
REDMINE_TGZ_URL=http://rubyforge.org/frs/download.php/73457/${REDMINE_TGZ}
REDMINE_SVN_URL=http://svn.redmine.org/redmine/tags/${REDMINE_VERSION}

RACK_VERSION=1.0.1
RAILS_VERSION=2.3.5

LOCAL_REDMINE_TGZ="$DOWNLOAD_CACHE/$REDMINE_TGZ"
LOCAL_REDMINE_DIR="$UNZIP_DIR/$REDMINE_DIR"

flake8 . || exit 1

unpack_gem() {
    GEM_NAME="$1"
    GEM_VERSION="$2"
    UNPACK_DIR="$3"
    GEM_FILE="$GEM_NAME-$GEM_VERSION.gem"
    LOCAL_GEM="$DOWNLOAD_CACHE/$GEM_FILE"
    if [[ ! -f "$LOCAL_GEM" ]]; then
        echo "Downloading the ${GEM_NAME}-${GEM_VERSION} gem..."
        (
            cd "$DOWNLOAD_CACHE"
            gem fetch ${GEM_NAME} -v "${GEM_VERSION}"
        )
    fi
    (
        cd "$UNPACK_DIR"
        gem unpack "$LOCAL_GEM"
    )
}

# Set the correct RVM ruby (1.8.7) if RVM is installed
if [[ $(which rvm > /dev/null) -eq 0 ]]; then
    if [[ $(type rvm | head -n 1 | grep -o function) == "function" ]]; then
        echo 'Loading the RVM script...'
        [[ -s "$HOME/.rvm/scripts/rvm" ]] && source "$HOME/.rvm/scripts/rvm"
    fi
    echo 'Setting Ruby to 1.8.7...'
    rvm use 1.8.7
fi

if [[ -z "$NO_SETUP_NEEDED" ]]; then
    if [[ -d "$LOCAL_REDMINE_DIR" ]]; then
        echo 'Re-creating Redmine install...'
        rm -r "$LOCAL_REDMINE_DIR"
    fi

    if [[ "$REDMINE_DOWNLOAD_METHOD" == "SVN" ]]; then
        svn co "$REDMINE_SVN_URL" "$LOCAL_REDMINE_DIR"
    else
        if [[ ! -f "$LOCAL_REDMINE_TGZ" ]]; then
            echo "Downloading Redmine ${REDMINE_VERSION} from the internet..."
            wget -O "$LOCAL_REDMINE_TGZ" "$REDMINE_TGZ_URL"
        fi
        tar -C "$UNZIP_DIR" -xf "$LOCAL_REDMINE_TGZ"
    fi

    cd "$LOCAL_REDMINE_DIR"
    # enable the REST API
    perl -0 -i -pe 's@(rest_api_enabled:\s+default:) 0@$1 1@msg' config/settings.yml
    cp "$BASE_DIR"/database.yml "$LOCAL_REDMINE_DIR"/config/
    if [[ "$REDMINE_DOWNLOAD_METHOD" == "SVN" ]]; then
        # Force install old rake
        gem uninstall rake
        gem install rake -v 0.8.7
        # if redmine comes from SVN, install rails too
        gem install rails -v "$RAILS_VERSION"
    else
        # install one gem locally
        unpack_gem rack $RACK_VERSION vendor/gems
    fi
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

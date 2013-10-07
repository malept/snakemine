#!/bin/bash

BASE_DIR="$(pwd)/$(dirname $0)"

if [[ -z "$DOWNLOAD_CACHE" ]]; then
    DOWNLOAD_CACHE=/tmp
fi

if [[ -z "$UNZIP_DIR" ]]; then
    UNZIP_DIR=/tmp
fi

REDMINE_DIR=redmine-1.0.4
REDMINE_TGZ=${REDMINE_DIR}.tar.gz
REDMINE_TGZ_URL=http://rubyforge.org/frs/download.php/73457/${REDMINE_TGZ}

LOCAL_REDMINE_TGZ="$DOWNLOAD_CACHE/$REDMINE_TGZ"
LOCAL_REDMINE_DIR="$UNZIP_DIR/$REDMINE_DIR"

flake8 .

if [[ -z "$NO_SETUP_NEEDED" ]]; then
    if [[ ! -f "$LOCAL_REDMINE_TGZ" ]]; then
        wget -O "$LOCAL_REDMINE_TGZ" "$REDMINE_TGZ_URL"
    fi

    if [[ -d "$LOCAL_REDMINE_DIR" ]]; then
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
    rake generate_session_store db:migrate db:fixtures:load
    script/runner 'Token.create!(:action => "api", :user_id => 2, :value => "1234abcd");
Issue.create!(:parent_issue_id => 1, :subject => "parent issue test", :tracker_id => 1, :project_id => 1, :description => "Parent issue test", :author_id => 3)'
else
    cd "$LOCAL_REDMINE_DIR"
fi

script/server --daemon --binding=127.0.0.1
sleep 5 # make sure the stupid server is ready to accept connections
(cd "$BASE_DIR"/.. && coverage run -m unittest discover; coverage report -m)
kill -9 `cat tmp/pids/server.pid`

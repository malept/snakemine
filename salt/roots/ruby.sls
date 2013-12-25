rvm:
  group:
    - present

rvm-deps:
  pkg.installed:
    - names:
      - bash
      - coreutils
      - gzip
      - bzip2
      - gawk
      - sed
      - curl
      - git-core
      - subversion

mri-deps:
  pkg.installed:
    - names:
      - build-essential
      - openssl
      - libreadline6
      - libreadline6-dev
      - curl
      - git-core
      - zlib1g
      - zlib1g-dev
      - libssl-dev
      - libyaml-dev
      - libsqlite3-0
      - libsqlite3-dev
      - sqlite3
      - libxml2-dev
      - libxslt1-dev
      - autoconf
      - libc6-dev
      - libncurses5-dev
      - automake
      - libtool
      - bison
      - subversion
      - ruby

install-old-rake:
  module.wait:
    - name: rvm.do
    - ruby: 1.8.7
    - command: "gem install rake -v 0.8.7 --no-ri --no-rdoc"
    - runas: vagrant
    - watch:
      - module: rubygems-1.4.2

remove-rubygems-bundler:
  module.wait:
    - name: rvm.do
    - ruby: "1.8.7@global"
    - command: "gem uninstall -x rubygems-bundler bundler bundler-unload rake"
    - runas: vagrant
    - watch:
      - rvm: ruby-1.8.7

rubygems-1.4.2:
  module.wait:
    - name: rvm.do
    - ruby: 1.8.7
    - command: "rvm rubygems 1.4.2"
    - runas: vagrant
    - watch:
      - module: remove-rubygems-bundler

ruby-1.8.7:
  rvm.installed:
    - default: True
    - user: vagrant
    - require:
      - pkg: rvm-deps
      - pkg: mri-deps
      - group: rvm

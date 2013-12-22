This project is hosted at GitHub_. I gladly accept pull requests. If
you contribute code, please also create tests for your modifications,
otherwise your request will not be accepted as quickly (I will most likely ask
you to add tests). It would probably also be in your best interests to add
yourself to the ``AUTHORS.rst`` file if you have not done so already.

.. _GitHub: https://github.com/malept/snakemine

A Vagrant_ environment is available for developing snakemine. Simply run the
following command (once Vagrant is installed)::

    $ vagrant up

...and it will install all of the Python dependencies in a virtualenv_, plus
set up a compatible Ruby environment for Redmine. You can then log into the
virtual machine::

    $ vagrant ssh
    vagrant@vagrant $ source .virtualenv/bin/activate

.. _Vagrant: https://www.vagrantup.com
.. _virtualenv: http://virtualenv.org/

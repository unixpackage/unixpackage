UnixPackage
===========

UnixPackage is a UNIX independent way of installing packages. Specify the
Ubuntu package name (e.g. libpq-dev), and it will install the equivalent
on your system (e.g. postgresql-libs on Arch).


Install
-------

Either::

  $ pip install unixpackage

Or::

  $ sudo pip install unixpackage

unixpackage is entirely self contained and has no dependencies. It is
safe to use sudo pip install with it.

Simple Usage
------------

Run::

  $ unixpackage install libpq-dev

On Arch this will run::

  $ sudo pacman -S postgresql-libs

On Debian and Ubuntu::

  $ sudo apt-get install libpq-dev

On Mac OS X::

  $ brew install postgresql

On Red Hat/CentOS/Fedora::

  $ sudo yum install postgresql-devel


Other usage
-----------

You can also just print the command to install rather than running it::

  $ unixpackage show libpq-dev libssl-dev
  sudo pacman -S postgresql-libs openssl

Or just check to see if it is installed::

  $ unixpackage check libpq-dev openssl
  Installed

Or install using "polite mode"::

  $ unixpackage install libpq-dev --polite
  The following command must be run to continue. I am attempting to run it now:


         sudo apt-get install -y libpq-dev


  You can also run this command in another window and then hit Ctrl-C to continue.

  [sudo] password for user:
  Reading package lists... Done
  Building dependency tree
  Reading state information... Done
  Suggested packages:
    postgresql-doc-9.3
  The following NEW packages will be installed:
    libpq-dev
  0 upgraded, 1 newly installed, 0 to remove and 0 not upgraded.
  Need to get 0 B/140 kB of archives.
  After this operation, 741 kB of additional disk space will be used.
  Selecting previously unselected package libpq-dev.
  (Reading database ... 231796 files and directories currently installed.)
  Preparing to unpack .../libpq-dev_9.3.9-0ubuntu0.14.04_amd64.deb ...
  Unpacking libpq-dev (9.3.9-0ubuntu0.14.04) ...
  Processing triggers for man-db (2.6.7.1-1ubuntu1) ...
  Setting up libpq-dev (9.3.9-0ubuntu0.14.04) ...
  Post-install package check for libpq-dev successful!


Python API
----------

There is also a python API for the above commands:

.. code-block:: python

    import unixpackage
    import sys

    # Install package if not already installed
    unixpackage.install(["libpq-dev"])

    # Install package if not already installed (in polite mode)
    unixpackage.install(["libpq-dev"], polite=True)

    # Check if packages are installed
    if unixpackage.packages_installed(["libpq-dev"]):
        sys.stdout.write("libpq-dev installed")




Package Library
---------------

Package names and their equivalents are downloaded from https://github.com/unixpackage/unixpackage.github.io via the generated website:

Example : http://unixpackage.github.io/libpq-dev.json

These files are cached in the ~/.unixpackage directory.

To add more packages you want to be installable in a UNIX-independent way,
fork and submit a pull request to this repository:
http://github.com/unixpackage/unixpackage.github.io



Want to help?
-------------

See CONTRIBUTING.rst

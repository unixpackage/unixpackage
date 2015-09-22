UnixPackage
===========

UnixPackage is a UNIX independent way of installing packages. Specify the
Ubuntu package name (e.g. libpq-dev), and it will install the equivalent
on your system (e.g. postgresql-libs on Arch).


Install
-------

Make sure that you have pip installed (any version). Then run::

  $ pip install unixpackage


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


Python API
----------

There is also a python API for the above commands:

.. code-block:: python

    import unixpackage
    import sys

    # Install package if not already installed
    unixpackage.install(["libpq-dev"])

    # Check if packages are installed
    if unixpackage.packages_installed(["libpq-dev"]):
        sys.stdout.write("libpq-dev installed")




Where does it get the package names from?
-----------------------------------------

Here : http://unixpackage.github.io/libpq-dev.json

To add packages, fork this repository and submit a pull request to this repository: http://github.com/unixpackage/unixpackage.github.io

Raising an issue if you want packages added is also welcome.

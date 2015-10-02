# -*- coding: utf-8 -*
from setuptools.command.install import install
from setuptools import find_packages
from setuptools import setup
import subprocess
import codecs
import sys
import os

def read(*parts):
    # intentionally *not* adding an encoding option to open
    # see here: https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    return codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), *parts), 'r').read()

setup(name="unixpackage",
      version="0.3.5",
      description="One command to install equivalent packages in Ubuntu, Debian, CentOS, Fedora, Red Hat and Mac OS X.",
      long_description=read('README.rst'),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
          'Operating System :: Unix',
          'Environment :: Console',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
      ],
      keywords='apt-get yum brew mac dpkg rpm unix package finder',
      author='Colm O\'Connor',
      author_email='colm.oconnor.github@gmail.com',
      url='https://github.com/unixpackage/unixpackage',
      license='AGPL',
      install_requires=[],
      packages=find_packages(exclude=[]),
      package_data={},
      entry_points=dict(console_scripts=['unixpackage=unixpackage:commandline.run',]),
      zip_safe=False,
      include_package_data=True,
)

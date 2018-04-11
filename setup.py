# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import io
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class Tox(TestCommand):
    def run_tests(self):
        import tox

        errno = -1
        try:
            tox.session.main()
        except SystemExit as e:
            errno = e.code
        sys.exit(errno)


class PyTest(TestCommand):
    def run_tests(self):
        import pytest

        errno = pytest.main()
        sys.exit(errno)

description = 'A plugin oriented tool for automating the investigation of broken hosts and services.'
try:
    with io.open('README.md', encoding="utf-8") as fh:
            long_description = fh.read()
except IOError:
    long_description = description

setup(
    name='fossor',
    version='1.1.2',
    description=description,
    long_description=description,
    url='https://github.com/linkedin/fossor',
    author='Steven R. Callister',
    author_email='scallist@linkedin.com',
    license='License :: OSI Approved :: BSD License',
    packages=find_packages(),
    install_requires=[
        'asciietch>=1.0.2',
        'click>=6.7',
        'psutil>=5.4.1',
        'setproctitle>=1.1.10',
        'requests>=2.18.4',
        'humanfriendly>=4.4.1',
        'parsedatetime>=2.4',
        'PTable>=0.9.2',
        'setuptools>=30',
    ],
    cmdclass={'test': PyTest,
              'pytest': PyTest,
              'tox': Tox,
              },
    tests_require=[
        'pytest>=3.0.6',
        'flake8>=3.5.0',
        'pytest-timeout>=1.2.0',
        'tox'
    ],
    entry_points={
        'console_scripts': [
            'fossor = fossor.cli:main',
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: POSIX :: Linux'
    ]
)

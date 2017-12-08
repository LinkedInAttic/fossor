# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import sys
import logging

from time import sleep

from fossor.checks.check import Check
from fossor.engine import Fossor


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)


class LongCheck(Check):
    def run(self, variables):
        self.log.info("Running long check")
        time_to_sleep = 60
        sleep(time_to_sleep)
        return "This plugin slept for {0} seconds".format(time_to_sleep)


class ShortCheck(Check):
    def run(self, variables):
        self.log.info("Running short check")
        time_to_sleep = 0
        return "This plugin slept for {0} seconds".format(time_to_sleep)


class FailCheck(Check):
    def run(self, variables):
        self.log.info("Running fail check")
        raise Exception("Testing plugin failure")


def test_one_fail_both_short_and_long_running_plugin():
    '''Confirm long running check will not show up in report'''
    f = Fossor()
    f.check_plugins = set()
    f.check_plugins = [LongCheck, ShortCheck]
    f.variable_plugins = set()
    f.add_variable('timeout', 1)
    f.add_variable('verbose', 'True')
    result = f.run(report='DictObject')

    assert 'Timed out' in result['LongCheck']
    assert 'This plugin slept' in result['ShortCheck']


def test_timeout_exception_and_success_for_plugins():
    '''Confirm long running check will not show up in report'''
    f = Fossor()
    f.check_plugins = set()
    f.check_plugins = [LongCheck, FailCheck, ShortCheck]
    f.variable_plugins = set()
    f.add_variable('timeout', 5)
    f.add_variable('verbose', 'True')
    result = f.run(report='DictObject')

    assert 'Timed out' in result['LongCheck']
    assert 'This plugin slept for' in result['ShortCheck']
    assert 'Failed' in result['FailCheck']


def test_long_running_plugin_verbose():
    '''Confirm long running check does show up in report with verbose on'''
    f = Fossor()
    f.check_plugins = set()
    f.check_plugins = [LongCheck]
    f.variable_plugins = set()
    f.add_variable('timeout', 1)
    f.add_variable('verbose', 'True')
    result = f.run(report='DictObject')
    log.debug(f"result is: {result}")
    assert 'Timed out' in result['LongCheck']


def test_long_running_plugin():
    '''Confirm long running check will not show up in report'''
    f = Fossor()
    f.check_plugins = set()
    f.check_plugins = [LongCheck]
    f.variable_plugins = set()
    f.add_variable('timeout', 1)
    f.add_variable('verbose', False)
    result = f.run(report='DictObject')
    log.debug(f"result is: {result}")
    assert 'LongCheck' not in result.keys()


def test_short_running_plugin():
    '''Confirm short running check will show up in report'''
    f = Fossor()
    f.check_plugins = set()
    f.check_plugins = [ShortCheck]
    f.variable_plugins = set()
    f.add_variable('verbose', True)
    result = f.run(report='DictObject')
    assert 'ShortCheck' in result.keys()

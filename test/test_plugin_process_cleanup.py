# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import sys
import psutil
import logging

from time import sleep
from unittest.mock import patch

from fossor.checks.check import Check
from fossor.engine import Fossor


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)

process_exceptions = (ProcessLookupError, PermissionError, psutil.AccessDenied, psutil.ZombieProcess, psutil.NoSuchProcess)


class LongCheck(Check):
    def run(self, variables):
        self.log.info("Running long check")
        time_to_sleep = 31.4
        out, err, ret = self.shell_call(f'sleep {time_to_sleep}')
        return "This plugin slept for {0} seconds".format(time_to_sleep)


def test_shell_call_properly_kills():
    f = Fossor()
    f.check_plugins = set()
    f.check_plugins = [LongCheck]
    f.variable_plugins = set()
    f.add_variable('timeout', 5)
    f.add_variable('verbose', 'True')
    result = f.run(report='DictObject')
    log.debug(f"result is: {result}")
    assert 'Timed out' in result['LongCheck']

    # Confirm that all processes were properly killed before Fossor exited
    for p in psutil.process_iter():
        try:
            assert 'sleep 31.4' != ' '.join(p.cmdline())
        except process_exceptions:
            continue


def test_shell_call_is_needed_to_kill():
    f = Fossor()
    f.check_plugins = set()
    f.check_plugins = [LongCheck]
    f.variable_plugins = set()
    f.add_variable('timeout', 5)
    f.add_variable('verbose', 'True')
    with patch('fossor.engine.Fossor._terminate_process_group'):
        result = f.run(report='DictObject')
    log.debug(f"result is: {result}")

    # Confirm fossor thinks the plugin ran too long
    assert 'Timed out' in result['LongCheck']

    # Confirm that the sleeping process outlasted lipy-fossor since we patched process group termination to do nothing
    sleeping_pids = []
    for p in psutil.process_iter():
        try:
            if 'sleep 31.4' == ' '.join(p.cmdline()):
                sleeping_pids.append(p)
        except process_exceptions:
            continue
    assert len(sleeping_pids) == 1

    # Clean-up pid by killing it and making sure it is gone
    pid = sleeping_pids[0]
    pid.kill()
    sleep(5)
    sleeping_pids = []
    for p in psutil.process_iter():
        try:
            if 'sleep 31.4' == ' '.join(p.cmdline()):
                sleeping_pids.append(p)
        except process_exceptions:
            continue
    assert len(sleeping_pids) == 0

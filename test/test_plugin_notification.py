# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import sys
import logging

from fossor.checks.check import Check
from fossor.engine import Fossor


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)


class FailCheck(Check):
    def run(self, variables):
        foo = "bar"
        raise Exception("Testing plugin failure")
        return foo


def test_crash_verbose():
    '''Check that the variable from the above class did show up in the report'''
    f = Fossor()
    f.check_plugins = set()
    f.check_plugins = [FailCheck]
    f.variable_plugins = set()
    f.add_variable('verbose', True)
    result = f.run(report='DictObject')

    output = result['FailCheck']

    assert 'Fail' in output
    # check that the variable foo and it's value of bar showed up in the output
    assert 'foo' in output
    assert 'bar' in output


def test_crash_not_verbose():
    '''Ensure crash report does not print when result should not be verbose.'''
    f = Fossor()
    f.check_plugins = set()
    f.check_plugins = [FailCheck]
    f.variable_plugins = set()
    f.add_variable('verbose', False)
    result = f.run(report='DictObject')
    result.pop('Stats')
    assert len(result) == 0

# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import sys
import json
import logging

from fossor.checks.check import Check
from fossor.engine import Fossor


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestCheck1(Check):
    def run(self, variables):
        return 'foo1'


class TestCheck2(Check):
    def run(self, variables):
        return 'foo2'


def test_json_report():
    f = Fossor()
    f.check_plugins = set()
    f.check_plugins = [TestCheck1, TestCheck2]
    f.variable_plugins = set()
    f.add_variable('verbose', True)

    json_result = f.run(report='Json')
    log.debug(f"json_result: {json_result}")

    object_result = json.loads(json_result)
    log.debug(f"object_result: {object_result}")
    assert 'TestCheck1' in object_result

    new_json_result = json.dumps(object_result)
    log.debug(f"new_json_result: {new_json_result}")

    assert 'TestCheck1' in new_json_result
    assert 'TestCheck1' in json_result

    assert 'TestCheck2' in new_json_result
    assert 'TestCheck2' in json_result

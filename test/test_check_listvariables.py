# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import sys
import logging
from fossor.checks.listvariables import ListVariables

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)


def test_listvariables_no_verbose():
    variables = {}
    lv = ListVariables()
    assert lv.run(variables) is None


def test_listvariables_verbose():
    variables = {}
    variables['verbose'] = True
    lv = ListVariables()
    assert lv.run(variables) == 'verbose=True'


def test_listvariables():
    variables = {}
    variables['verbose'] = True
    variables['foo'] = 'foo'
    variables['foobar'] = False

    lv = ListVariables()
    output = lv.run(variables)
    assert 'verbose=True' in output
    assert 'foo=foo' in output
    assert 'foobar=False' in output

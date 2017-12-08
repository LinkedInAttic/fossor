# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import sys
import logging

import fossor

from fossor.engine import Fossor

import fossor.variables.hostname
import fossor.checks.buddyinfo

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)


def test_plugin_import_by_module():
    f = Fossor()
    f.clear_plugins()
    f.add_plugins(fossor)

    assert fossor.checks.buddyinfo.BuddyInfo in f.check_plugins
    assert fossor.variables.examplevariable.ExampleVariable in f.variable_plugins

    assert 'BuddyInfo' in [p.get_name() for p in f.check_plugins]
    assert 'fossor.checks.buddyinfo.BuddyInfo' in [p.get_full_name() for p in f.check_plugins]


def test_plugin_import_by_path():
    f = Fossor()
    f.clear_plugins()

    f.add_plugins(fossor.__path__[0])

    assert 'BuddyInfo' in [p.get_name() for p in f.check_plugins]
    assert 'fossor.local.checks.buddyinfo.BuddyInfo' in [p.get_full_name() for p in f.check_plugins]

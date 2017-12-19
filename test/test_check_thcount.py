# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

from unittest.mock import patch

from fossor.checks.thcount import Thcount


@patch('fossor.plugin.Plugin.shell_call')
def test_thcount(sc_mock):
    out = 'THCNT USER\n1 root\n2 ermanuel\n1001 scallist\n10000 fossor \n1 fossor\n1 root\n1 root\n1 root\n1 root\n1 root\n1 root'
    err = ''
    return_code = 0

    sc_mock.return_value = out, err, return_code
    c = Thcount()
    assert c.run({}) == 'user fossor currently has 10001 threads\n'

# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

from unittest.mock import patch

from fossor.checks.netiface_errors import NetIFace


def test_parse_sar():
    """Ensures stdout is appropriately merged into the datastructure."""

    input = 'Average:         ppp0      5.00      49152.00      2064.00      64738.00      2064.00      4096.00      0.00      0.00      0.00'
    sar = NetIFace()._parse_sar(input)

    assert sar.rxerr == '5.00'
    assert sar.txerr == '2064.00'
    assert sar.rxdrop == '64738.00'
    assert sar.txdrop == '2064.00'
    assert sar.txcarr == '4096.00'


@patch('fossor.plugin.Plugin.shell_call')
@patch('platform.system')
@patch('os.path.isdir')
def test_disk_usage(isdir_mock, system_mock, sc_mock):
    """Validate the response from for run() is correct."""
    out = 'Average:         ppp0      0.00      0.00      0.00      0.00      1.00      0.00      0.00      0.00      0.00'
    err = ''
    return_code = 0

    system_mock.return_value = 'Linux'
    isdir_mock.return_value = True
    sc_mock.return_value = out, err, return_code

    c = NetIFace().run({})
    assert c == 'stat=txdrop, interface=ppp0 has surpassed threshold. value=1.0\n'

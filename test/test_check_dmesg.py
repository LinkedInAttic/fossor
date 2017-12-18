# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import sys
import logging
from io import StringIO
from importlib import reload
from fossor.checks import dmesg
from unittest.mock import patch

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)

example_dmesg_output = '''[2047964.712926] usb 2-1.3.4: New USB device strings: Mfr=1, Product=2, SerialNumber=3
[2047964.712929] usb 2-1.3.4: Product: Pixel
[2047964.712934] usb 2-1.3.4: SerialNumber: FA6CM0300679
[2052025.266882] usb 2-1.3.4: USB disconnect, device number 39
[2062321.522490] usb 2-1.3.4: new high-speed USB device number 40 using ehci-pci
[2062321.610727] usb 2-1.3.4: New USB device found, idVendor=18d1, idProduct=4ee1
[2062321.610732] usb 2-1.3.4: New USB device strings: Mfr=1, Product=2, SerialNumber=3
[2062321.610735] usb 2-1.3.4: Product: Pixel
[2062321.610739] usb 2-1.3.4: SerialNumber: FA6CM030067'''


def test_dmesg():
    with patch('fossor.utils.misc.common_path', return_value='/usr/bin/dmesg'):
        reload(dmesg)
        variables = {}
        d = dmesg.Dmesg()
        with patch('fossor.plugin.Plugin.shell_call') as mocked_shell_call:
            text = StringIO(initial_value=example_dmesg_output)
            mocked_shell_call.return_value = (text, '', 0)
            result = d.run(variables)
            assert 'high-speed' in result


def test_dmesg_with_start_end_times():
    variables = {}
    variables['start_time'] = 1509647158.0
    variables['end_time'] = 1509647160.0
    with patch('fossor.utils.misc.common_path', return_value='/usr/bin/dmesg'):
        reload(dmesg)
        d = dmesg.Dmesg()
        with patch('fossor.plugin.Plugin.shell_call') as mocked_shell_call:
            with patch('fossor.checks.dmesg.Dmesg._get_boot_time') as mocked_get_boot_time:
                mocked_get_boot_time.return_value = 1509664739.8043845 - 2069605.89
                text = StringIO(initial_value=example_dmesg_output)
                mocked_shell_call.return_value = (text, '', 0)
                result = d.run(variables)
                assert 'USB disconnect, device number 39' in result
                assert len(result.splitlines()) == 1

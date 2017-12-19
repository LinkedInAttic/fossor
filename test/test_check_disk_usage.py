# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

from unittest.mock import patch

from fossor.checks.diskusage import DiskUsage


@patch('fossor.plugin.Plugin.shell_call')
def test_disk_usage(sc_mock):
    out = 'Filesystem     1K-blocks      Used Available Use% Mounted on\n' \
          '/dev/sda2       407G  318G   69G  99% /\n' \
          'tmpfs            32G  161M   32G   1% /dev/shm'
    err = ''
    return_code = 0

    sc_mock.return_value = out, err, return_code
    c = DiskUsage()
    assert c.run({}) == 'Disk utilization is at critical state (> 98). partition=/dev/sda2 at utilization=99%'

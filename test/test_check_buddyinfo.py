# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

from unittest.mock import patch

from fossor.checks.buddyinfo import BuddyInfo


@patch('fossor.checks.buddyinfo.BuddyInfo._getpagesize')
@patch('fossor.plugin.Plugin.shell_call')
def test_buddyinfo_report(sc_mock, pagesize_mock):
    expected = """\
No significant memory fragmentation
Smallest Page Size for system is 4096
Therefore, each columns pagesize is: 4 KiB 8 KiB 16 KiB 32 KiB 64 KiB 128 KiB 256 KiB 512 KiB 1 MiB 2 MiB 4 MiB
Output of 'cat /proc/buddyinfo' is:
Node 0, zone      DMA      2      1      1      1      1      0      1      0      1      1      3
Node 0, zone    DMA32   2592   2028   1683   1408   1060    689    423    220    115     18      0
Node 0, zone   Normal  74469  83969 174582 227090 116398  48054  23129  13454   6410      2      0"""
    out = """\
Node 0, zone      DMA      2      1      1      1      1      0      1      0      1      1      3
Node 0, zone    DMA32   2592   2028   1683   1408   1060    689    423    220    115     18      0
Node 0, zone   Normal  74469  83969 174582 227090 116398  48054  23129  13454   6410      2      0"""
    err = ''
    return_code = 0

    sc_mock.return_value = out, err, return_code
    pagesize_mock.return_value = 4096
    buddy = BuddyInfo()
    result = buddy.run({})
    assert result == expected


@patch('fossor.checks.buddyinfo.BuddyInfo._getpagesize')
@patch('fossor.plugin.Plugin.shell_call')
def test_buddyinfo_fragmentation(sc_mock, pagesize_mock):
    out = """\
Node 0, zone      DMA      2      1      1      1      1      0      1      0      1      1      3
Node 0, zone    DMA32   2592   2028   1683   1408   1060    689    423    220    115     18      0
Node 0, zone   Normal  74469  83969      0      0      0      0      0      0      0      0      0"""
    err = ''
    return_code = 0

    sc_mock.return_value = out, err, return_code
    pagesize_mock.return_value = 4096
    buddy = BuddyInfo()
    buddy.run({})
    assert buddy.fragmentation()


@patch('fossor.plugin.Plugin.shell_call')
def test_get_page_size(sc_mock):
    out = '4096'
    err = ''
    return_code = 0

    sc_mock.return_value = out, err, return_code
    buddy = BuddyInfo()
    assert buddy._getpagesize() == 4096

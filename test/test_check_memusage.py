# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

from unittest.mock import patch


@patch('platform.system')
@patch('fossor.checks.memusage.MemUsage.get_meminfo')
@patch('fossor.checks.memusage.MemUsage.get_time')
@patch('fossor.plugin.Plugin.shell_call')
@patch('fossor.utils.misc.common_path', return_value='/usr/bin/dmesg')
def test_mem_usage(cp_mock, sc_mock, time_mock, mem_mock, ps_mock):
    from fossor.checks.memusage import MemUsage

    line1 = '[11686.040460] flasherav invoked oom-killer: gfp_mask=0x201da, order=0, oom_adj=0, oom_score_adj=0'
    line2 = '[4680581.563150] perl invoked oom-killer: gfp_mask=0x380da, order=0, oom_score_adj=0'
    line3 = '[4680582.563150] perl invoked oom-killer: gfp_mask=0x380da, order=0, oom_score_adj=0'

    booted = 1503084682.520215
    cutoff = 4670863.29

    MEM_TOTAL = 100
    MEM_IN_USE = 50

    meminfo = {}
    meminfo['MemTotal'] = MEM_TOTAL
    meminfo['MemFree'] = MEM_TOTAL - MEM_IN_USE
    meminfo['Buffers'] = 0
    meminfo['Cached'] = 0

    out = ''
    err = ''
    return_code = 0
    os_name = "Darwin"

    sc_mock.return_value = out, err, return_code
    mem_mock.return_value = meminfo
    ps_mock.return_value = os_name

    c = MemUsage()

    # Memusage within memusage.MemUsage.CRITICAL_TRESH == OK
    assert c.run({}) is None

    os_name = "Linux"
    ps_mock.return_value = os_name
    assert c.run({}) is None

    # Memusage outside of threshold == WARN
    meminfo['MemFree'] = 5
    assert c.run({}) == 'High Memory Use!\nMemTotal: 100 kib\nUsed: 95 kib (95%)'

    # Memusage outside of threshold, with oom-killer present == WARN
    out = '{}\n{}\n{}'.format(line1, line2, line3)
    sc_mock.return_value = out, err, return_code
    time_mock.return_value = booted, cutoff
    assert c.run({}) == (
        'High Memory Use!\nMemTotal: 100 kib\nUsed: 95 kib (95%)'
        '\n\noom-killer present in dmesg | tail!'
        '\nWed, 11 Oct 2017 23:41:04[4680581.563150] perl invoked oom-killer: gfp_mask=0x380da, order=0, oom_score_adj=0\n'
        'Wed, 11 Oct 2017 23:41:05[4680582.563150] perl invoked oom-killer: gfp_mask=0x380da, order=0, oom_score_adj=0\n'

        )

    # Memusage within threshold, but with oom-killer present == WARN
    meminfo['MemFree'] = MEM_TOTAL - MEM_IN_USE
    assert c.run({}) == (
        'High Memory Use!\nMemTotal: 100 kib\nUsed: 50 kib (50%)'
        '\n\noom-killer present in dmesg | tail!'
        '\nWed, 11 Oct 2017 23:41:04[4680581.563150] perl invoked oom-killer: gfp_mask=0x380da, order=0, oom_score_adj=0\n'
        'Wed, 11 Oct 2017 23:41:05[4680582.563150] perl invoked oom-killer: gfp_mask=0x380da, order=0, oom_score_adj=0\n'
        )

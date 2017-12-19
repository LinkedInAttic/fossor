# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import time
import re
import platform
from fossor.checks.check import Check
from fossor.utils.misc import common_path


class MemUsage(Check):
    """This Check inspects the current memory usage and will alert the
    user if it seems excessive"""

    def run(self, variables):
        os_name = platform.system()
        if os_name != "Linux":
            return

        # Critical memory-in-use threshold %
        CRITICAL_THRESH = 90
        meminfo = self.get_meminfo()

        act_free = meminfo['MemFree'] + meminfo['Buffers'] + meminfo['Cached']
        used = meminfo['MemTotal'] - act_free
        perc_used = (used/meminfo['MemTotal'])*100

        out, err, return_code = self.shell_call(common_path(['/usr/bin/dmesg', '/bin/dmesg']))

        if perc_used >= CRITICAL_THRESH or 'oom-killer' in out:
            res = 'High Memory Use!\nMemTotal: {0:.0f} kib\nUsed: {1:.0f} kib ({2:.0f}%)'.format(
                meminfo['MemTotal'], used, perc_used)

            if 'oom-killer' in out:
                res = res + '\n\noom-killer present in dmesg | tail!\n{}'.format(self.get_ooms(out))

            return res

    def get_meminfo(self):
        meminfo = {}
        with open('/proc/meminfo') as m:
            for i in m.readlines():
                meminfo[i.split()[0].rstrip(':')] = int(i.split()[1])

        return meminfo

    def get_time(self):
        now = time.time()
        up = float(open('/proc/uptime').read().split()[0])
        booted = now - up
        cutoff = up - 86400
        return booted, cutoff

    def get_ooms(self, out):
        booted, cutoff = self.get_time()
        newline = ""

        for line in out.split('\n'):
            if 'oom-killer' in line:
                t = re.match("^\[(\d+.\d+)\]", line)
                if t:
                    human_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime(booted + float(t.group(1))))
                    if float(t.group(1)) > cutoff:
                        newline = newline + human_time + line + "\n"

                else:
                    return '\n'.join([line for line in out.split('\n') in line])

        return newline


if __name__ == '__main__':
    m = MemUsage()
    print(m.run({}))

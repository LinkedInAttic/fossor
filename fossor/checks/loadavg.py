# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import os
from fossor.checks.check import Check


class LoadAvg(Check):
    '''this Check will compare the current load average summaries against the count of CPU cores
    in play, and will alert the user if there are more processes waiting'''
    def run(self, variables):
        ON_LINUX = os.path.isdir('/proc')
        if ON_LINUX:
            with open('/proc/loadavg') as f:
                contents = f.read().strip()
                load_summaries = [float(i) for i in contents.split()[:3]]
            with open('/proc/cpuinfo') as f:
                cpu_count = len([c for c in f.read().splitlines() if c.startswith('processor')])
        else:
            uptime, err, return_code = self.shell_call('uptime')
            contents = uptime.strip()
            load_summaries = [float(i.replace(',', '')) for i in contents.split()[-3:]]

            cpu, err, return_code = self.shell_call('sysctl -n hw.ncpu')
            cpu_count = int(cpu.strip())
        # Alert the user if any of the 1, 5, or 15-minute load averages is greater than the processor count to handle them
        if any(c / cpu_count > 1 for c in load_summaries):
            return 'Load average shows processes queued beyond CPU count!\nCPU Count: {0}\nLoad averages: {1}'.format(
                cpu_count,
                ' '.join(str(x) for x in load_summaries)
            )


if __name__ == '__main__':
    l = LoadAvg()
    print(l.run({}))

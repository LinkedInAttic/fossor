# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

from fossor.checks.check import Check


class DiskUsage(Check):
    """DiskUsage ensures that disk utilization percentage for any mounted partitions
    remains under PERCENTAGE_ALERT ."""

    PERCENTAGE_ALERT = 98

    def run(self, variables):

        out, err, return_code = self.shell_call('df')
        disk_free = out.splitlines()[1:]
        exceeded = []
        for row in disk_free:
            mount = row.split()
            partition = mount[0]
            percentage = int(mount[4].replace('%', ''))

            if percentage >= DiskUsage.PERCENTAGE_ALERT:
                exceeded.append('partition={0} at utilization={1}%'.format(partition, percentage))

        if exceeded:
            return 'Disk utilization is at critical state (> {0}). {1}'.format(DiskUsage.PERCENTAGE_ALERT, ','.join(exceeded))


if __name__ == '__main__':
    c = DiskUsage()
    print(c.run({}))

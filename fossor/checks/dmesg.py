# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import re
import sys
import time
import logging

from datetime import datetime, timedelta
from fossor.checks.check import Check
from fossor.utils.misc import iswithintimerange, common_path

TIME_FORMAT = '%b %d %H:%M:%S'


class Dmesg(Check):

    def run(self, variables):
        start_time = variables.get('start_time', None)
        end_time = variables.get('end_time', None)

        result = self._getdmesgoutput(start_time=start_time, end_time=end_time)
        if result:
            return result

    def _getdmesgoutput(self, start_time=None, end_time=None):
        result = []
        out, err, returncode = self.shell_call(common_path(['/usr/bin/dmesg', '/bin/dmesg']), stream=True)
        boot_time = self._get_boot_time()

        dmesg_pattern = re.compile('\[(.*?)\] (.*)')

        for line in out:
            m = dmesg_pattern.match(line)
            dmesg_time = m.group(1).strip()
            timestamp = boot_time + float(dmesg_time)
            if iswithintimerange(timestamp, start_time, end_time):
                message = m.group(2)
                dt = datetime.fromtimestamp(timestamp)
                date_str = dt.strftime('%Y/%m/%d %H:%M:%S')
                result.append(' '.join([date_str, message]))

        if result:
            result.reverse()
            return '\n'.join(result)

    def _get_boot_time(self):
        with open('/proc/uptime') as f:
                uptime = float(f.read().split()[0])
        boot_time = time.time() - uptime
        return boot_time


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    variables = {}
    variables['start_time'] = (datetime.now() - timedelta(seconds=3600 * 24)).timestamp()
    variables['end_time'] = datetime.now().timestamp()
    d = Dmesg()
    result = d.run(variables)
    if result:
        print(result)
    else:
        print("No recent messages in dmesg. Add a test message like this for quick local testing: echo 'test message' | sudo tee /dev/kmsg")

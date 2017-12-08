# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import os
import platform

from datetime import datetime, timedelta
from collections import namedtuple

from fossor.checks.check import Check, UnsupportedPlatformException


class NetIFace(Check):
    """NetIFace polls SARs EDEV (network error) statistics and notifies if
    stat > ERROR_THRESHOLD.

    EDEV: statistics on failures (errors) from the network devices are reported"""

    NIC_STATS = {
        # Total number of bad packets received per second
        'rxerr': 0,
        # Total number of errors that happened per second while transmitting packets
        'txerr': 0,
        # Number of received packets dropped per second because of a lack of space in linux buff.
        'rxdrop': 0,
        # Number of transmitted packets dropped per second because of a lack of space in linux buffers
        'txdrop': 0,
        # Number of carrier-errors (link) that happened per second while transmitting packets.
        'txcarr': 0,
    }

    def _parse_sar(self, stdout):
        """Massage stdout from subprocess.Popen in the Sar namedtuple. Errors worth keeping are defined
        within NetIFace.NIC_STATS

        :param stdout: str of data received from subprocess.Popen."""

        Sar = namedtuple('Sar', 'rxerr, coll, txerr, rxdrop, txdrop, txcarr')
        return Sar(*stdout.split()[2:8])

    def run(self, variables):
        """Default `Check` plug-in entry point.

        :param variables: A dict representing user defined variables.
                          'nic' : network interface (default=bond0)
                          'minutes': number of minutes to look back. Default = 60, max=43200 """

        # pull in global variables or configure sane defaults for SAR time window.
        # sar -[se] switches only allow for a 24 hour window. This check will further shrink
        # the allowed window to 12 hours.
        nic = variables.get('nic', 'bond0')
        minutes = int(variables.get('minutes', 60))

        if minutes > 43200 or minutes < 0:
            minutes = 60

        start_time = (datetime.now() + timedelta(minutes=-minutes)).strftime('%H:%M:%S')
        end_time = datetime.now().strftime('%H:%M:%S')

        # this check relies on data massaged via SAR and therefore Linux only.
        if platform.system() != 'Linux':
            raise UnsupportedPlatformException('{platform} is not supported by {module}'.format(
                                               platform=platform.system(), module=self.__class__.__name__))

        # ensure that nic is plumbed and active on the system
        if not os.path.isdir('/proc/sys/net/ipv4/conf/{nic}'.format(nic=nic)):
            raise UnsupportedPlatformException('NIC={nic} not present on your platform'.format(nic=nic))

        cmd = 'sar -n EDEV -s {start} -e {end}|grep "Average.*{nic}"'.format(nic=nic, start=start_time, end=end_time)
        self.log.debug('executing cmd={0}'.format(cmd))

        out, err, return_code = self.shell_call(cmd)
        nic_stats = out

        if not nic_stats:
            return

        sar = self._parse_sar(nic_stats)
        result = ''

        for stat in NetIFace.NIC_STATS:
            val = float(getattr(sar, stat))
            if val > NetIFace.NIC_STATS[stat]:
                result += 'key={key}, interface={nic} has surpassed threshold. value={val}\n'.format(
                          key=stat, nic=nic, val=val)
        return result


if __name__ == '__main__':
    c = NetIFace()
    print(c.run({'nic': 'eth0', 'minutes': '64738'}))
    print(c.run({'nic': 'eth0', 'minutes': '-1'}))
    print(c.run({'nic': 'eth0'}))

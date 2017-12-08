# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import platform

from datetime import datetime, timedelta
from collections import namedtuple

from fossor.checks.check import Check


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

    def run(self, variables: dict):
        """Check for Network Interface Errors using Sar data"""

        # pull in global variables or configure sane defaults for SAR time window.
        # sar -[se] switches only allow for a 24 hour window. This check will further shrink
        # the allowed window to 12 hours.
        minutes = int(variables.get('minutes', 60))

        if minutes > 43200 or minutes < 0:
            minutes = 60

        start_time = (datetime.now() + timedelta(minutes=-minutes)).strftime('%H:%M:%S')
        end_time = datetime.now().strftime('%H:%M:%S')

        # this check relies on data massaged via SAR and therefore Linux only.
        if platform.system() != 'Linux':
            return

        cmd = f'/usr/bin/sar -n EDEV -s {start_time} -e {end_time}'
        self.log.debug(f'executing cmd={cmd}')

        out, err, return_code = self.shell_call(cmd)
        nic_stats = out

        # Get just averages
        nic_stats = [line for line in nic_stats.splitlines() if line.startswith('Average')]

        if not nic_stats:
            self.log.debug("No nics found.")
            return
        for line in nic_stats:
            sar = self._parse_sar(line)
            result = ''

            nic = line.split()[1]

            for stat in NetIFace.NIC_STATS:
                val = float(getattr(sar, stat))
                if val > NetIFace.NIC_STATS[stat]:
                    result += f'stat={stat}, interface={nic} has surpassed threshold. value={val}\n'
            return result

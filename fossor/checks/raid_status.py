# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import os
import re

from fossor.checks.check import Check


class RaidStatus(Check):

    def run(self, variables: dict):
        '''Check if there are any drives down in a Raid Array.'''
        mdstat_location = '/proc/mdstat'
        if not os.path.exists(mdstat_location):
            self.log.debug(f"{mdstat_location} does not exist.")
            return
        with open(mdstat_location, 'rt') as f:
            mdstat = f.read()

        arrays = re.findall('\[[U_]+\]', mdstat)
        for array in arrays:
            if '_' in array:
                message = f"Drives down in Raid Array ({array})\n"
                message += f"{mdstat_location} output:\n"
                message += f"{mdstat}"
                return message

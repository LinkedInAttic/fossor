# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import psutil
from fossor.variables.variable import Variable


class LogFiles(Variable):
    def run(self, variables):
        pid = variables.get('Pid', None)
        if not pid:
            return

        p = psutil.Process(pid)
        log_files = None

        try:
            log_files = [x.path for x in p.open_files() if x.path.lower().endswith('.log')]
        except psutil.AccessDenied:
            self.log.warn(f"Did not have permission to retrieve open files for process {pid}")

        if log_files:
            return log_files

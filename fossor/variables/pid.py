# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import os
import psutil

from fossor.variables.variable import Variable
from fossor.utils.misc import psutil_exceptions


class Pid(Variable):
    def run(self, variables):
        product = variables.get('Product', None)
        if product:
            for p in psutil.process_iter():
                try:
                    if product.lower().startswith(p.name().lower()):
                        return p.pid
                except psutil_exceptions:
                    continue


class PidCwd(Variable):
    def run(self, variables):
        pid = variables.get('Pid', None)
        if pid:
            try:
                return os.readlink(f'/proc/{pid}/cwd')
            except PermissionError:
                pass


class PidExe(Variable):
    def run(self, variables):
        pid = variables.get('Pid', None)
        if pid:
            try:
                return os.readlink(f'/proc/{pid}/exe')
            except PermissionError:
                pass

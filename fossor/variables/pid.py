# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import os
import psutil

from fossor.variables.variable import Variable
from fossor.utils.misc import psutil_exceptions


class Pid(Variable):
    def run(self, variables):
        if 'Product' not in variables:
            return
        product = variables['Product']
        for p in psutil.process_iter():
            try:
                if product.startswith(p.name()):
                    return p.pid
            except psutil_exceptions:
                continue


class PidCwd(Variable):
    def run(self, variables):
        if 'Pid' in variables:
            try:
                return os.readlink('/proc/{pid}/cwd'.format(pid=variables['Pid']))
            except PermissionError:
                pass


class PidExe(Variable):
    def run(self, variables):
        if 'Pid' in variables:
            try:
                return os.readlink('/proc/{pid}/exe'.format(pid=variables['Pid']))
            except PermissionError:
                pass

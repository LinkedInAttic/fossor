# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

from fossor.variables.variable import Variable
import os


class Cwd(Variable):
    def run(self, variables):
        if 'Pid' in variables:
            return os.readlink('/proc/{pid}/cwd'.format(pid=variables['Pid']))


class Exe(Variable):
    def run(self, variables):
        if 'Pid' in variables:
            return os.readlink('/proc/{pid}/exe'.format(pid=variables['Pid']))

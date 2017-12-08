# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

from fossor.variables.variable import Variable
import socket


class Hostname(Variable):
    def run(self, variables):
        return socket.getfqdn()

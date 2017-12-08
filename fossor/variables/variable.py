# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

# Template variable class
from abc import abstractmethod
from fossor.plugin import Plugin


class Variable(Plugin):

    @abstractmethod
    def run(self, variables):
        '''variable should be a dict of variables with values'''
        pass

# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

# Template check class
from abc import abstractmethod
from fossor.plugin import Plugin


class Check(Plugin):

    @abstractmethod
    def run(self, variables):
        '''Variables should be a dict of variables. By default, will only report if something is outputted.'''
        pass

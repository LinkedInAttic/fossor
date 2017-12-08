# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

from fossor.variables.variable import Variable


class ExampleVariable(Variable):
    def run(self, variables: dict):
        '''If an object is returned from this method, it will be saved as a variable'''
        if 'Debug' not in variables:
            return
        if variables['Debug'] is True:
            self.log.debug("Logging example")
            return "This is an example variable that only returns when Debug is True."

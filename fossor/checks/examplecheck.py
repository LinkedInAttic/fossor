# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

from fossor.checks.check import Check


class ExampleCheck(Check):

    def run(self, variables: dict):
        '''If a string returned from  this method, it will be reported as "interesting" output for this plugin'''
        if 'Debug' not in variables:
            return
        if variables['Debug'] is True:
            self.log.debug("Logging example")
            return 'This is an example of a check plugin. It only prints when Debug is True.'

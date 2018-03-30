# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

from fossor.checks.check import Check


class ListVariables(Check):

    def run(self, variables):
        '''If verbose is on, list all variables in use'''
        verbose = variables.get('verbose', None)
        if verbose:
            result = [f"{name}={value}" for name, value in variables.items()]
            return "\n".join(result)

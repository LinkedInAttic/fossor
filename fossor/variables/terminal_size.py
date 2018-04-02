# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

from fossor.variables.variable import Variable
from fossor.reports.report import TABLE_FORMATTING_WIDTH


class TerminalWidth(Variable):
    def run(self, variables):
        '''Whatever string is returned from here will be saved as a variable'''
        out, err, return_code = self.shell_call('stty size')
        try:
            rows, columns = out.split()
            return int(columns)
        except ValueError:
            # No stty.  Most likely running headless
            return 132


class MaxPluginOutputWidth(Variable):
    def run(self, variables):
        '''If plugins keep their output width under this amount, they won't be truncated.'''
        terminal_width = variables.get('TerminalWidth', None)
        if terminal_width:
            return terminal_width - TABLE_FORMATTING_WIDTH

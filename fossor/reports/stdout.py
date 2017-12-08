# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

# Cli Report
from fossor.reports.report import Report


class StdOut(Report):
    def run(self, variables, report_input, **kwargs):
        if 'TerminalWidth' in variables:
            kwargs['width'] = int(variables['TerminalWidth'])
        timeout = variables['timeout'] if 'timeout' in variables else 600
        truncate = variables.get('truncate', True)
        if truncate:
            kwargs['max_lines_per_plugin'] = 20
        debug = variables['debug'] if 'debug' in variables else False

        # If in debug mode, don't print line by line, print all at once in the print statement below instead
        # This prevents logs lines becoming interspersed with the report.
        stdout = not debug

        result = self.create_report_text(report_input, timeout=timeout, stdout=stdout, truncate=truncate, **kwargs)
        if debug:
            print(result)  # Print the report now that the massive amount of logging has finished
        return result

# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

# Returns a dict object. Currently used in unit tests, but could be helpful when interacting with Fossor as a library.
from fossor.reports.report import Report


class DictObject(Report):
    def run(self, variables, report_input, **kwargs):
        result = {}
        while True:
            name, output = report_input.get()
            if name == 'EOF':
                break
            result[name] = output
        return result

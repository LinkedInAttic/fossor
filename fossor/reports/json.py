# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

# Returns a json string object.

import json

from fossor.reports.report import Report
from fossor.reports.dict_object_report import DictObject


class Json(Report):
    def run(self, variables, report_input, **kwargs):
        do = DictObject()
        dict_report = do.run(variables, report_input, **kwargs)
        json_str = json.dumps(dict_report, sort_keys=True, indent=4)
        print(json_str)
        return json_str

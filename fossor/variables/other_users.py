# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

from fossor.variables.variable import Variable
from getpass import getuser


class OtherUsers(Variable):
    """Checks for other users logged into the host box other than the current user."""
    def run(self, variables):
        # Users that we consider "uninteresting" so we won't return them.
        boring_users = [getuser(), 'root', 'app']
        out, err, return_code = self.shell_call('users')
        other_users = sorted(set(out.split()) - set(boring_users))

        if len(set(out.split()) - set(boring_users)) > 0:
            return ' '.join(str(u) for u in other_users)

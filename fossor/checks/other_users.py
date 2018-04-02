# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

from fossor.checks.check import Check


class OtherUsers(Check):
    """Checks for other users logged into the host box other than the current user."""
    def run(self, variables):
        other_users = variables.get('OtherUsers', None)
        if other_users:
            msg = 'Other users logged into this box: '
            user_list = ', '.join(str(u) for u in other_users.split())
            return msg + user_list + '\n'

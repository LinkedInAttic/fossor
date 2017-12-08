# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

from fossor.checks.check import Check
from collections import defaultdict


class Thcount(Check):
    '''Simple thread count via ps.  Arbitrarily set to 10k threads'''
    def run(self, variables):
        tc = defaultdict(int)
        rd = ""
        out, err, return_code = self.shell_call('ps -e -o thcount,user')
        ps = out.splitlines()
        for pid in ps:
            count, user = pid.split()
            if count.isdigit():
                tc[user] += int(count)

        for user in tc:
            if tc[user] > 10000:
                rd = rd + 'user {0} currently has {1} threads\n'.format(user, tc[user])
                return rd


if __name__ == '__main__':
    t = Thcount()
    print(t.run({}))

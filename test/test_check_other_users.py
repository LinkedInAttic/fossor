# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

from fossor.checks.other_users import OtherUsers


def test_check_other_users():
    variables = {}
    variables['OtherUsers'] = 'phfry brodriguez tleela'
    c = OtherUsers()

    # Test for multiple users logged in
    assert c.run(variables) == 'Other users logged into this box: phfry, brodriguez, tleela\n'

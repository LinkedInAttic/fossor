# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

from unittest.mock import patch
from fossor.variables.other_users import OtherUsers


@patch('fossor.variables.other_users.getuser')
@patch('fossor.plugin.Plugin.shell_call')
def test_other_users(sc_mock, user_mock):
    current_user = 'brodriguez'
    user_mock.return_value = current_user
    c = OtherUsers()
    err = ''
    return_code = 0

    # Test for multiple users logged in
    users1 = [current_user, 'pfry', 'hfarnsworth', 'root', 'app']
    out1 = ' '.join(str(u) for u in users1)
    sc_mock.return_value = out1, err, return_code
    assert c.run({}) == 'hfarnsworth pfry'

    # Test for single user logged in
    users2 = [current_user]
    out2 = ' '.join(str(u) for u in users2)
    sc_mock.return_value = out2, err, return_code
    assert c.run({}) is None

    # Test for single user logged in, multiple sessions
    users3 = [current_user, current_user, current_user]
    out3 = ' '.join(str(u) for u in users3)
    sc_mock.return_value = out3, err, return_code
    assert c.run({}) is None

    # Test for single user and other "not interesting users" logged in
    users4 = [current_user, 'root', 'app']
    out4 = ' '.join(str(u) for u in users4)
    sc_mock.return_value = out4, err, return_code
    assert c.run({}) is None

# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import sys
import time
import logging
import unittest

from datetime import datetime
from unittest.mock import patch
from fossor.checks.dmesg import Dmesg
from fossor.utils.misc import iswithintimerange
from fossor.utils.misc import comparetimerange

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestTimeWithinRange(unittest.TestCase):

    def test_is_none(self):
        t = time.time()
        start = t - 5
        end = t + 5
        assert comparetimerange(t=None, start_time=start, end_time=end) is None
        assert iswithintimerange(t=None, start_time=start, end_time=end) is None

        # Same test with datetimes
        t = datetime.fromtimestamp(t)
        start = datetime.fromtimestamp(start)
        end = datetime.fromtimestamp(end)
        assert iswithintimerange(t=None, start_time=start, end_time=end) is None

    def test_within_range(self):
        t = time.time()
        start = t - 5
        end = t + 5
        assert iswithintimerange(t=t, start_time=start, end_time=end) is True

        # Same test with datetimes
        t = datetime.fromtimestamp(t)
        start = datetime.fromtimestamp(start)
        end = datetime.fromtimestamp(end)
        assert iswithintimerange(t=t, start_time=start, end_time=end) is True

    def test_before_range(self):
        # Test before range
        t = time.time()
        start = t + 5
        end = t + 10
        assert iswithintimerange(t=t, start_time=start, end_time=end) is False

        # Same test with datetimes
        t = datetime.fromtimestamp(t)
        start = datetime.fromtimestamp(start)
        end = datetime.fromtimestamp(end)
        assert iswithintimerange(t=t, start_time=start, end_time=end) is False

    def test_after_range(self):
        t = time.time()
        start = t - 10
        end = t - 5
        assert iswithintimerange(t=t, start_time=start, end_time=end) is False

        # Same test with datetimes
        t = datetime.fromtimestamp(t)
        start = datetime.fromtimestamp(start)
        end = datetime.fromtimestamp(end)
        assert iswithintimerange(t=t, start_time=start, end_time=end) is False


def test_get_variables():
    '''Confirm we get the correct variables back if an exception occurs.'''
    with patch('fossor.plugin.Plugin.shell_call') as patched_shell_call:
        patched_shell_call.side_effect = Exception('foobar')
        d = Dmesg()
        variables = {}
        variables['verbose'] = True
        result = d.run_helper(variables)
        assert "args: ('/usr/bin/dmesg',)" in result

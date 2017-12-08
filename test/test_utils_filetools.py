# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import os
import sys
import logging
import time

from datetime import datetime
from io import StringIO
from fossor.utils.filetools import FileTools
from unittest.mock import patch

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)


def test_get_first_last_lines():
    # Using bytes instead of strings since BytesIO I'm using to mock filehandle operations requires this.
    first_line = 'first line\n'
    middle_line = 'middle line\n'
    last_line = 'last line\n'
    data = first_line + middle_line + last_line

    f = StringIO()
    f.write(data)
    orig_pos = f.tell()

    ft = FileTools()
    first, last = ft.get_first_last_lines(f)
    assert orig_pos == f.tell()  # Assert file_handle position returned to where it was originally
    assert first_line == first
    assert last_line == last


def test_get_first_last_lines_empty_line():
    data = ''

    f = StringIO()
    f.write(data)
    orig_pos = f.tell()

    ft = FileTools()
    first, last = ft.get_first_last_lines(f)
    assert orig_pos == f.tell()  # Assert file_handle position returned to where it was originally
    assert first == ''
    assert last == ''


def test_get_first_last_lines_almost_empty():
    data = '\n'

    f = StringIO()
    f.write(data)
    orig_pos = f.tell()

    ft = FileTools()
    first, last = ft.get_first_last_lines(f)
    assert orig_pos == f.tell()  # Assert file_handle position returned to where it was originally
    assert first == '\n'
    assert last == '\n'


def test_get_current_line():
    ft = FileTools()
    text = '\ntest1\ntest2\n'

    log.debug(f"\ntext: {repr(text)}")
    handle = StringIO(text)

    handle.seek(0, os.SEEK_SET)
    line = ft._get_current_line(handle)
    assert line == '\n'
    assert handle.tell() == 0

    # Get 'test1\n' by starting at every single character
    # Each iteration should return 'test1\n'
    for i in range(1, 7):
        handle.seek(i)
        line = ft._get_current_line(handle)
        assert line == 'test1\n'
        assert handle.tell() == 1

    # Test readline then previous line to make sure they return the same line
    handle.seek(1)
    line = handle.readline()
    assert line == 'test1\n'
    line = ft._get_previous_line(handle)
    assert line == 'test1\n'
    assert handle.tell() == 1

    # Get 'test2\n' by starting at every single character
    for i in range(7, 12):
        handle.seek(i)
        line = ft._get_current_line(handle)
        assert line == 'test2\n'
        assert handle.tell() == 7

    # Test without newline at the beginning
    text = 'test1\ntest2\n'
    log.debug(f"\ntext: {repr(text)}")
    handle = StringIO(text)
    for i in range(0, 6):  # Get 'test1\n' by starting at every single character
        handle.seek(i)
        line = ft._get_current_line(handle)
        assert line == 'test1\n'
        assert handle.tell() == 0


def test_get_previous_line():
    ft = FileTools()
    text = ''
    now = time.time()
    for i in range(50):
        dt = datetime.fromtimestamp(now + i)
        dt_str = dt.strftime(ft.date_format)
        # Adding snowman unicode character to test to ensure this doesn't break by reading the middle of a unicode character
        text += f"{dt_str} INFO Snowman-unicode-character:☃ message #{i}\n"

    log.debug(f"\ntext: {repr(text)}")
    handle = StringIO(text)
    handle.seek(0, os.SEEK_END)  # Seek to the last character in the file
    for i in range(49, -1, -1):  # Print messages in reverse order from 49 down to 0. Middle -1 is exclusive, so means 0 in this case.
        line = ft._get_previous_line(handle)
        assert f'message #{i}' in line


def test_gettimestamp():
    ft = FileTools()
    text = ''
    now = int(time.time())
    for i in range(50):
        dt = datetime.fromtimestamp(now + i)
        dt_str = dt.strftime(ft.date_format)
        if i == 19:
            dt_str = '2017/MalformedDate'
        text += f"{dt_str} INFO message #{i}\n"

    log.debug(f"text: {text}")
    handle = StringIO(text)
    for i in range(50):
        if i == 19:
            assert ft._gettimestamp(line=handle.readline()) is None
        else:
            assert now + i == ft._gettimestamp(line=handle.readline())
    assert ft.date_length is not None


def test_binary_search():
    ft = FileTools()
    text = ''
    now = int(time.time())
    for i in range(50):
        dt = datetime.fromtimestamp(now + i)
        dt_str = dt.strftime(ft.date_format)
        text += f"{dt_str} INFO message #{i}\n"

    log.debug(f"text: {text}")
    handle = StringIO(text)

    log.debug("Testing 20/30")
    start_time = now + 20
    end_time = now + 30
    pos = ft._get_first_log_line_position_binary_search(file_handle=handle, start_time=start_time, end_time=end_time)
    handle.seek(pos)
    line = handle.readline()
    log.debug(f"20/30 pos: {pos}. line: {line}")
    assert 'message #20' in line

    log.debug("Testing 0/10")
    start_time = now
    end_time = now + 10
    pos = ft._get_first_log_line_position_binary_search(file_handle=handle, start_time=start_time, end_time=end_time)
    handle.seek(pos)
    line = handle.readline()
    log.debug(f" 0/10 pos: {pos}. line: {line}")
    assert 'message #0' in line

    log.debug("Testing 45/47")
    start_time = now + 45
    end_time = now + 47
    pos = ft._get_first_log_line_position_binary_search(file_handle=handle, start_time=start_time, end_time=end_time)
    handle.seek(pos)
    line = handle.readline()
    log.debug(f" 45/47 pos: {pos}. line: {line}")
    assert 'message #45' in line

    log.debug("Testing -10/-5")
    start_time = now - 10
    end_time = now - 5
    pos = ft._get_first_log_line_position_binary_search(file_handle=handle, start_time=start_time, end_time=end_time)
    log.debug(f" -10/-5 pos: {pos}")
    assert pos is None

    log.debug("Testing 55/60")
    start_time = now + 55
    end_time = now + 60
    pos = ft._get_first_log_line_position_binary_search(file_handle=handle, start_time=start_time, end_time=end_time)
    log.debug(f" 55/60 pos: {pos}")
    assert pos is None


def test_binary_search_malformed():
    ft = FileTools()
    text = ''
    now = int(time.time())
    for i in range(50):
        dt = datetime.fromtimestamp(now + i)
        dt_str = dt.strftime(ft.date_format)
        if i in range(0, 5) or i in range(15, 20) or i in range(45, 50):
            dt_str = '2017/MalformedDate'
        text += f"{dt_str} INFO message #{i}\n"

    log.debug(f"text: {text}")
    handle = StringIO(text)

    log.debug("Testing 20/30")
    start_time = now + 20
    end_time = now + 30
    pos = ft._get_first_log_line_position_binary_search(file_handle=handle, start_time=start_time, end_time=end_time)
    handle.seek(pos)
    line = handle.readline()
    log.debug(f"20/30 pos: {pos}. line: {line}")
    assert 'message #20' in line

    log.debug("Testing 0/10")
    start_time = now
    end_time = now + 10
    pos = ft._get_first_log_line_position_binary_search(file_handle=handle, start_time=start_time, end_time=end_time)
    handle.seek(pos)
    line = handle.readline()
    log.debug(f" 0/10 pos: {pos}. line: {line}")
    assert 'message #5' in line

    log.debug("Testing 45/47")
    start_time = now + 45
    end_time = now + 47
    pos = ft._get_first_log_line_position_binary_search(file_handle=handle, start_time=start_time, end_time=end_time)
    log.debug(f" 45/47 pos: {pos}.")
    assert pos is None

    log.debug("Testing -10/-5")
    start_time = now - 10
    end_time = now - 5
    pos = ft._get_first_log_line_position_binary_search(file_handle=handle, start_time=start_time, end_time=end_time)
    log.debug(f" -10/-5 pos: {pos}")
    assert pos is None

    log.debug("Testing 55/60")
    start_time = now + 55
    end_time = now + 60
    pos = ft._get_first_log_line_position_binary_search(file_handle=handle, start_time=start_time, end_time=end_time)
    log.debug(f" 55/60 pos: {pos}")
    assert pos is None


def test_get_logs_in_time_range():
    ft = FileTools()
    now = int(time.time())

    def _generate_handle_text(start, end):
        handle_text = ''
        for i in range(start, end):
            dt = datetime.fromtimestamp(now + i)
            dt_str = dt.strftime(ft.date_format)
            handle_text += f"{dt_str} INFO message #{i}\n"
        return handle_text

    handle1_text = _generate_handle_text(0, 5)
    handle2_text = _generate_handle_text(10, 15)
    handle3_text = _generate_handle_text(20, 25)

    with patch('fossor.utils.filetools.FileTools._open_log_file') as mo:
        def _mocked_open(*args, **kwargs):
            '''Return mocked handle text if opening specific file_paths, otherwise use the original builtin.open'''
            text = None
            if 'handle1' in args:
                text = handle1_text
            elif 'handle2' in args:
                text = handle2_text
            elif 'handle3' in args:
                text = handle3_text

            if text:
                f = StringIO()
                f.write(text)
                f.seek(0, os.SEEK_SET)
                return f
        mo.side_effect = _mocked_open
        log_generator = ft.get_logs_in_time_range(file_paths=['handle1', 'handle2', 'handle3'])
        lines = [line for line in log_generator]
        for line in lines:
            log.debug(f"timestamp: {ft._gettimestamp(line)}. line: {repr(line)}")
        assert 'message #0\n' in lines[0]
        assert 'message #24\n' in lines[-1]

        # Test sorting
        log_generator = ft.get_logs_in_time_range(file_paths=['handle3', 'handle1', 'handle2'], start_time=None, end_time=None)
        lines = [line for line in log_generator]
        assert 'message #0\n' in lines[0]
        assert 'message #24\n' in lines[-1]

        # Test trimming by time ranges
        log_generator = ft.get_logs_in_time_range(file_paths=['handle3', 'handle1', 'handle2'], start_time=now + 11, end_time=now + 13)
        lines = [line for line in log_generator]
        assert 'message #11\n' in lines[0]
        assert 'message #13\n' in lines[-1]

        log_generator = ft.get_logs_in_time_range(file_paths=['handle3', 'handle1', 'handle2'], start_time=now + 3, end_time=now + 13)
        lines = [line for line in log_generator]
        assert 'message #3\n' in lines[0]
        assert 'message #13\n' in lines[-1]

        log_generator = ft.get_logs_in_time_range(file_paths=['handle3', 'handle1', 'handle2'], start_time=now + 13, end_time=now + 23)
        lines = [line for line in log_generator]
        assert 'message #13\n' in lines[0]
        assert 'message #23\n' in lines[-1]

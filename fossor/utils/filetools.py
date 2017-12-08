# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import os
import gzip
import logging

from datetime import datetime

from fossor.utils.misc import comparetimerange, iswithintimerange


class FileTools(object):

    def __init__(self, date_format=None):
        self.log = logging.getLogger(__name__)

        self.date_format = '%Y-%m-%dT%H:%M:%S.%f'  # default date format - ISO 8601.
        if date_format:
            self.date_format = date_format
        self.date_length = None

    def get_first_last_lines(self, file_handle):
        original_position = file_handle.tell()

        file_handle.seek(os.SEEK_SET)
        first = file_handle.readline()

        file_handle.seek(0, os.SEEK_END)
        last = self._get_previous_line(file_handle=file_handle)
        file_handle.seek(original_position)
        return first, last

    def _gettimestamp(self, line) -> float:
        '''Uses the FileTools.date_format object to pull a timestamp from a line
           Will attempt to trim line to date using FileTools.date_length'''
        date_str = line[:self.date_length] if self.date_length else line
        try:
            dt = datetime.strptime(date_str, self.date_format)
            if dt.year == 1900:  # Year was missing and defaulted to 1900
                dt = dt.replace(year=datetime.now().year)
            return dt.timestamp()
        except ValueError as e:
            error_message = e.args[0]
            if 'does not match format' in error_message:
                return None
            elif 'unconverted data remains: ' in error_message:
                unconverted_data = error_message.split('unconverted data remains: ')[1]
                if not self.date_length:
                    self.date_length = len(line) - len(unconverted_data)
                    return self._gettimestamp(line)  # Try again one time now that we have a length for the date_str
                else:
                    raise e

    def _open_log_file(self, file_path):
        '''Determine if file is gzipped or not, and then return an appropriate file handle.'''
        try:
            f = gzip.open(file_path, 'rt')
            f.readline()  # Try reading a line to check if this is a gzipped file
            f.seek(0, os.SEEK_SET)  # Return seek position to beginning
            return f
        except (IOError, OSError):
            f = open(file_path, 'rt')
            return f

    def _get_previous_line(self, file_handle) -> str:
        '''Returns the previous line, even if the current seek position is in the middle of a line.
           Seek position will be placed at the first character of the returned line.
           If at the beginning of a file, the first line will be returned.'''
        f = file_handle
        self._get_current_line(file_handle=f)
        new_position = max(0, f.tell() - 2)  # Go to 1 past the current newline
        f.seek(new_position)
        return self._get_current_line(file_handle=f)

    def _get_current_line(self, file_handle) -> str:
        '''Returns the current line by seeking leftwards to the first newline or beginning of file.
           Seek position will be placed at first character of the returned line.'''
        f = file_handle
        orig_pos = f.tell()
        f = file_handle
        curr_pos = orig_pos
        while curr_pos > 0:
            curr_pos -= 1
            f.seek(curr_pos)
            try:
                char = f.read(1)
                if '\n' in char:
                    curr_pos = f.tell()  # Reset the curr_pos to just after the newline
                    break
            except UnicodeDecodeError:  # Incase we read the middle of a unicode character instead of the beginning of it
                pass  # Next pass will move one byte to the left and try to read again
        f.seek(curr_pos)
        line = f.readline()
        f.seek(curr_pos)
        return line

    def _get_first_log_line_position_binary_search(self, file_handle, start_time, end_time) -> int:
        '''Return seek position of first log line in the time range specified.'''
        f = file_handle
        eof = f.seek(0, os.SEEK_END)
        end = eof
        start = f.seek(0, os.SEEK_SET)
        earliest_pos_in_range = None
        while True:
            curr_pos = int((start + end) / 2)
            f.seek(curr_pos)

            if start == end:
                break  # We're at the start or end of the file

            # Get to the beginning of the line
            line = self._get_current_line(f)
            dateless_lines_allowed = 200
            for lines_without_dates in range(dateless_lines_allowed + 1):
                line = f.readline()
                line_comparison = comparetimerange(self._gettimestamp(line), start_time=start_time, end_time=end_time)

                if line_comparison is not None or not f.tell() < eof:
                    self._get_previous_line(f)  # reset cursor back to beginning of the line we got from readline
                    line_start = f.tell()
                    break

            if lines_without_dates >= dateless_lines_allowed:
                raise ValueError(f"Couldn't find line with valid time format in {dateless_lines_allowed} lines")
            elif line_comparison is None:  # File does not contain lines within time range
                break
            elif line_comparison == 0:  # Current line is within the time range
                earliest_pos_in_range = line_start
                end = curr_pos
            elif line_comparison < 0:  # Current line is earlier than the time range
                start = min(curr_pos + 1, end)
            elif line_comparison > 0:  # Current line is later than the time range
                end = max(curr_pos - 1, start)

        timestamp = self._gettimestamp(line)
        self.log.debug(f"Earliest line in range {start_time}-{end_time} at position: {earliest_pos_in_range} with timestamp: {timestamp}. Line: {repr(line)}")
        return earliest_pos_in_range

    def get_logs_in_time_range(self, file_paths, start_time=None, end_time=None):
        timestamped_lines = self.get_logs_in_time_range_with_timestamps(file_paths=file_paths, start_time=start_time, end_time=end_time)
        return (line for timestamp, line in timestamped_lines)

    def get_logs_in_time_range_with_timestamps(self, file_paths, start_time=None, end_time=None):
        '''Return a generator that provides the log lines within the specified times.
           Orders files based on timestamp present in first log line if available.
           Lines not matching FileTools.date_format will not be returned.'''

        file_handles = []
        for file_path in file_paths:
            f = self._open_log_file(file_path)
            first, last = self.get_first_last_lines(f)

            first_timestamp = self._gettimestamp(first)
            last_timestamp = self._gettimestamp(last)

            # Skip the file if the timestamps aren't in the right range
            if not iswithintimerange(first_timestamp, start_time=None, end_time=end_time):
                self.log.debug(f"Skipping file {file_path} since first timestamp in file {first_timestamp} is after the end_time: {end_time}")
                continue
            if not iswithintimerange(last_timestamp, start_time=start_time, end_time=None):
                self.log.debug(f"Skipping file {file_path} since last timestamp in file {first_timestamp} is before the start_time: {start_time}")
                continue

            file_handles.append((f, first_timestamp))

        file_handles.sort(key=lambda x: x[1])
        file_handles = [f for f, timestamp in file_handles]  # Remove the timestamps so file_handles is storing sorted file_handles without timestamps now.

        for f in file_handles:
            pos = self._get_first_log_line_position_binary_search(file_handle=f, start_time=start_time, end_time=end_time)
            f.seek(pos)
            for line in f:
                timestamp = self._gettimestamp(line)
                if iswithintimerange(timestamp, start_time=start_time, end_time=end_time):
                    yield timestamp, line
                else:
                    continue

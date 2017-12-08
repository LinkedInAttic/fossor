# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

from fossor.checks.check import Check
import humanfriendly


class BuddyInfo(Check):
    '''Checks for memory fragmentation using the /proc/buddyinfo file'''
    def __init__(self):
        self.zero_threshold = 9

    def run(self, variables):
        out, err, return_code = self.shell_call('cat /proc/buddyinfo')
        self.buddy_info_raw = out
        self.buddy_info_lines = [line for line in self.buddy_info_raw.split('\n') if 'Normal' in line]
        result = ''
        if self.fragmentation():
            result += "Possible memory fragmentation\n"
        else:
            result += "No significant memory fragmentation\n"
        result += f"Smallest Page Size for system is {self._getpagesize()}\n" \
                  f"Therefore, each columns pagesize is: {self._get_column_sizes_human_readable()}\n"
        result += "Output of 'cat /proc/buddyinfo' is:\n" + self.buddy_info_raw
        return result

    def _get_column_sizes_human_readable(self):
        column_count = self._get_columns_len()
        page_size = self._getpagesize()
        column_sizes = []
        for c in range(0, column_count):
            size = humanfriendly.format_size((2**c) * page_size, binary=True)
            column_sizes.append(size)

        return ' '.join(column_sizes)

    def _getpagesize(self):
        '''Return int of the page size for OS'''
        out, err, return_code = self.shell_call('getconf PAGE_SIZE')
        return int(out.strip())

    def _get_columns_len(self):
        '''Get number of columns for first row'''
        for line in self.buddy_info_lines:
            values_str = line.split('Normal')[1]
            columns = values_str.split()
            return len(columns)

    def should_notify(self):
        return self.fragmentation()

    def fragmentation(self):
        for line in self.buddy_info_lines:
            # line example 'Node 0, zone   Normal   1372  95320  85260  28831  45988  38962  24612  15433   8342     85   2723 '
            values_str = line.split('Normal')[1]
            values = [int(value) for value in values_str.split()]
            zero_values = [value for value in values if value < 1]
            if len(zero_values) >= self.zero_threshold:
                return True
        return False


if __name__ == "__main__":
    bi = BuddyInfo()
    print(bi.run(variables={}))

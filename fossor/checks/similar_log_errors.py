# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

from difflib import SequenceMatcher
from multiprocessing import Pool, cpu_count
from collections import OrderedDict

from fossor.checks.check import Check


class SimilarLogErrors(Check):
    '''Return uncommon errors from the logs'''

    # TODO add table formatting to show diffs over time?

    SIMILARITY_RATIO = 0.7  # Lines but be at least 70% similar in order to be counted.
    MAX_COMMON_LINES = 20  # Only track similarity ratios for up to 20 lines.

    # Logs matching these strings will not be included
    log_name_blacklist = ['_configuration.log',
                          '.out',
                          'gc.log',
                          'oor.log',
                          '_databus.log',
                          '_public_access.log',
                          'jetty_thread_pool_stats.log',
                          'engine_access_log.log',
                          ]

    def run(self, variables):
        result = ''

        log_files = variables.get('LogFiles', None)
        if not log_files:
            return

        log_files = self._remove_blacklisted_logs(log_files)
        self.log.debug(f"log_files: {log_files}")

        max_pool_threads = cpu_count() * 2
        pool = Pool(max_pool_threads)
        pool_results = pool.map(self.get_error_pattern_counts, log_files)

        for filename, common_lines in pool_results:
            lines = []
            for line, values in common_lines.items():  # Sort by count
                count = values['count']
                first_seen = values.get('first_seen', None)
                first_seen_text = ''
                if first_seen:
                    first_seen_text = f"First seen: {first_seen}, "
                count_text = f"Count: {count}, "
                line_text = f"{line.strip()}"
                text = first_seen_text + count_text + line_text
                lines.append(text)
            if lines:
                result += f"filename: {filename}\n"
                result += '\n'.join(lines) + '\n\n'

        if result:
            return result

    def _remove_blacklisted_logs(self, log_files):
        '''Remove blacklisted log_files'''
        for blacklisted_string in self.log_name_blacklist:
            log_files = [x for x in log_files if blacklisted_string not in x]

        return log_files

    def get_error_pattern_counts(self, filename):
        common_lines = OrderedDict()
        self.log.debug(f"Processing filename: {filename}")
        f = open(filename, 'rt')
        for line in f.readlines():
            line, date = self._process_line(line)
            if not line:
                continue

            # Group similar log lines
            common_lines = self._group_similar_log_lines(line=line, date=date, common_lines=common_lines)

        self.log.debug(f"Finished processing filename: {filename}")
        return filename, common_lines

    def _process_line(self, line):
        '''Returns line and timestamp from line, returns None if line should be ignored'''
        date = None
        first_character = line[0]

        # Skip certain log lines
        # Skip since this is the lower portion of a stacktrace
        if first_character.isspace():
            line = None
        # Line did not start with a date
        elif first_character.isalpha() and 'Exception' not in line:
            line = None
        elif line.startswith('Caused by'):
            line = None
        # Check for date and error level
        elif first_character.isdigit():
            line_split = line.split()
            try:
                line_level = line_split[2]
                if line_level != 'ERROR':
                    line = None
                else:
                    line = ' '.join(line_split[2:])  # Remove date portion from line
                    date = ' '.join(line_split[:2])
                    # Truncate line
                    line = f"{line:.200}"
            except IndexError as e:
                self.log.debug(f"IndexError parsing line: {line}")
                line = None
        return line, date

    def _group_similar_log_lines(self, line, date, common_lines):
        highest_similarity_ratio = 0
        most_similar_line = None
        for common_line in common_lines.keys():
            similarity_ratio = SequenceMatcher(a=common_line, b=line).quick_ratio()
            # Find the most similar line
            if similarity_ratio > highest_similarity_ratio:
                highest_similarity_ratio = similarity_ratio
                most_similar_line = common_line

        # Count the line if it is similar to another line
        if highest_similarity_ratio > self.SIMILARITY_RATIO:
            self.log.debug(f"Line had a ratio of {highest_similarity_ratio}, incrementing count. New line: {line}, Old line: {most_similar_line}")
            line = most_similar_line
        # Do we already have too many unique lines?
        elif len(common_lines) >= self.MAX_COMMON_LINES:
            line = 'Other Error Lines'
            self.log.debug(f"Too many unique lines, {len(common_lines)} of {self.MAX_COMMON_LINES}, adding this to category: {line}")

        self.log.debug(f"Line {line} had a ratio of {highest_similarity_ratio} which was under the threshold of {self.SIMILARITY_RATIO}, counting this line as unique.")
        values = common_lines.setdefault(line, {})
        values['count'] = values.get('count', 0) + 1
        if date:
            values.setdefault('first_seen', date)
        return common_lines

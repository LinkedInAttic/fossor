# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

from difflib import SequenceMatcher
from multiprocessing import Pool, cpu_count

from fossor.checks.check import Check


class SimilarLogErrors(Check):
    '''Return uncommon errors from the logs'''

    # TODO add table formatting to show diffs over time?

    SIMILARITY_RATIO = 0.7
    MAX_COMMON_LINES = 20

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
            for line, count in sorted(common_lines.items(), reverse=True, key=lambda x: x[1]):  # Sort by count
                lines.append(f"Count: {count}. {line.strip()}")
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
        common_lines = {}
        self.log.debug(f"Processing filename: {filename}")
        f = open(filename, 'rt')
        for line in f.readlines():
            line = self._process_line(line)
            if not line:
                continue

            # Group similar log lines
            common_lines = self._group_similar_log_lines(line=line, common_lines=common_lines)

        self.log.debug(f"Finished processing filename: {filename}")
        return filename, common_lines

    def _process_line(self, line):
        first_character = line[0]

        # Skip certain log lines
        # Skip since this is the lower portion of a stacktrace
        if first_character.isspace():
            return
        # Line did not start with a date
        elif first_character.isalpha() and 'Exception' not in line:
            return
        elif line.startswith('Caused by'):
            return
        # Check for an error level
        elif first_character.isdigit():
            line_split = line.split()
            try:
                line_level = line_split[2]
            except IndexError as e:
                self.log.debug(f"IndexError parsing line: {line}")
                return
            if line_level != 'ERROR':
                return
            line = ' '.join(line_split[2:])  # Remove date portion from line
        # Truncate line
        line = f"{line:.200}"
        return line

    def _group_similar_log_lines(self, line, common_lines):
        highest_similarity_ratio = 0
        most_similar_line = None
        for common_line in common_lines:
            similarity_ratio = SequenceMatcher(a=common_line, b=line).quick_ratio()
            if similarity_ratio > highest_similarity_ratio:
                highest_similarity_ratio = similarity_ratio
                most_similar_line = common_line

        if highest_similarity_ratio > self.SIMILARITY_RATIO:
            common_lines[most_similar_line] += 1
        elif len(common_lines) < self.MAX_COMMON_LINES:
            common_lines[line] = 1
        else:
            common_lines.setdefault('Other Error Lines', 0)
            common_lines['Other Error Lines'] += 1
        return common_lines

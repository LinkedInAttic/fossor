# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import statistics

from asciietch.graph import Grapher

from fossor.checks.check import Check
from fossor.utils.filetools import FileTools
import fossor.utils.anomaly_detection


class SystemLogVolume(Check):

    def __init__(self):
        self.syslog_format = '%b  %d %H:%M:%S'
        self.log_files = [('/var/log/messages', self.syslog_format),
                          ('/var/log/secure', self.syslog_format),
                          ('/var/log/cron', self.syslog_format),
                          ('/var/log/maillog', self.syslog_format),
                          ('/var/log/spooler', self.syslog_format),
                          ]

    def run(self, variables: dict):
        '''Print back system graphs if log volume has changed significantly.'''
        start_time = variables.get('start_time', None)
        end_time = variables.get('end_time', None)
        max_width = variables.get('MaxPluginOutputWidth', None)

        file_line_counts = self.get_line_counts(start_time, end_time)
        g = Grapher()
        result = ''
        for file_path, timestamped_values in file_line_counts:
            if not timestamped_values:
                continue

            values = [value for timestamp, value in timestamped_values.items()]
            if not fossor.utils.anomaly_detection.abnormal_distribution(values, ignore_zero=True):
                continue
            if statistics.mean(values) < 10:
                continue

            graph = g.asciigraph(values=timestamped_values, max_width=max_width, max_height=7, label=True)
            tmp = f"{file_path}:\n{graph}"
            result = '\n'.join([result, tmp])

        return result

    def get_line_counts(self, start_time, end_time):
        file_line_counts = []
        for file_path, date_format in self.log_files:
            line_counts = self.get_file_line_counts(file_path=file_path, date_format=date_format, start_time=start_time, end_time=end_time)
            file_line_counts.append((file_path, line_counts))
        return file_line_counts

    def get_file_line_counts(self, file_path, date_format, start_time=None, end_time=None):
        line_counts = {}
        ft = FileTools()

        ft.date_format = date_format

        try:
            log_lines = ft.get_logs_in_time_range_with_timestamps(file_paths=[file_path], start_time=start_time, end_time=end_time)
            for timestamp, line in log_lines:
                line_counts[timestamp] = line_counts.setdefault(timestamp, 0) + 1
        except PermissionError:
            self.log.warn(f"Did not have permission to access {file_path}")
        except FileNotFoundError:
            self.log.warn(f"{file_path} not found.")
        return line_counts

# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

# Template Report Class
import prettytable

from fossor.utils.misc import StatusPrinter
from fossor.plugin import Plugin


TABLE_FORMATTING_WIDTH = 4  # Global so other plugins can know the width of the table formatting and truncate themselves appropriately if needed.

# TODO Add start/end times to the report


class Report(Plugin):
    def run(self, variables, report_input, **kwargs):
        '''Expects a queue holding tuples like these ('name', 'output'). Expects EOF in name or value for queue termination.'''
        pass

    def create_report_text(self, input_queue, timeout, width=None, max_lines_per_plugin=None, truncate=True, stdout=False):
        '''Default report format, can be overridden'''
        # TODO add an option to table remove formatting

        if not width:
            width = 150

        result = []
        seperator = self._create_box_seperator(width)

        def add_line(text):
            if stdout:
                print(text)
            result.append(text)

        add_line(seperator)
        add_line(self._create_box_middle(text='Report', width=width, align='c'))
        add_line(seperator)

        status_printer = StatusPrinter(max_width=width, timeout=timeout)
        while True:
            status_printer.start()
            name, output = input_queue.get()
            status_printer.stop()

            if name == 'EOF':
                break

            if truncate:
                max_width = width - TABLE_FORMATTING_WIDTH
                output = self._truncate(text=output, max_width=max_width, max_height=max_lines_per_plugin)

            # Plugin Name
            add_line(self._create_box_middle(text=f"Plugin: {name}", width=width, height=max_lines_per_plugin))

            # Plugin Output
            add_line(seperator)
            add_line(self._create_box_middle(text=output, width=width, height=max_lines_per_plugin))
            add_line(seperator)

        # Close the queue
        input_queue.close()

        return '\n'.join(result)

    def _create_box(self, text, width, align='l'):
        result = ''
        result += self._create_box_seperator(width=width) + "\n"
        result += self._create_box_middle(text=text, width=width, align=align) + "\n"
        result += self._create_box_seperator(width=width) + "\n"
        return result

    def _create_box_seperator(self, width):
        return '+' + '-' * (width - 2) + '+'

    def _create_box_middle(self, text, width=None, height=None, align='l'):
        '''Default report format, can be overridden'''

        t = prettytable.PrettyTable()
        t.hrules = prettytable.NONE
        t.header = False
        t.field_names = ['foo']
        t.align = align
        # max width must be set after field_names
        t.min_width = width
        t.max_width = width
        t.min_table_width = width
        t.max_table_width = width
        t.add_row([text])
        return t.get_string()

    def _truncate(self, text, max_width=None, max_height=None):
        if max_height:
            # Truncate line count
            text_lines = [x for x in text.splitlines()]
            original_height = len(text_lines)
            if len(text_lines) > max_height:
                text_lines = text_lines[:max_height]
            new_height = len(text_lines)
            text = '\n'.join(text_lines)
            if new_height != original_height:
                text += f'\nTruncated line count from {original_height} to {new_height}. Run with --no-truncate to stop truncation.'

        if max_width:
            text_split = text.splitlines()
            long_line_count = len([line for line in text_split if len(line) > max_width])
            # Truncate line length to fit in table
            if long_line_count > 0:
                text = '\n'.join([x[:max_width] for x in text_split])
                text += f'\nTruncated {long_line_count} lines to a width of {max_width}. Run with --no-truncate to stop truncation.'

        return text

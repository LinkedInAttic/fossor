#!/usr/bin/env python
# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.


from __future__ import absolute_import
from __future__ import print_function

import sys
import click
import logging
import setproctitle
import parsedatetime as pdt
from datetime import datetime, timedelta
from fossor.engine import Fossor

default_plugin_dir = '/opt/fossor'


@click.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True, help_option_names=['-h', '--help']))  # noqa: C901
@click.pass_context
@click.option('-p', '--product', help="Product to investigate.")
@click.option('--pid', help="Pid to investigate.")
@click.option('--plugin-dir', default=default_plugin_dir, help=f'Import all plugins from this directory. Default dir: {default_plugin_dir}')
@click.option("--days", default=2, help="Start from X days ago, defaults to 2 days. Plugins may optionally implement and use this.")
@click.option('--start-time', default='', help='Plugins may optionally implement and use this.')
@click.option('--end-time', default='', help='Plugins may optionally implement and use this. Defaults to now.')
@click.option('-t', '--time-out', default=600, help='Default timeout for plugins.')
@click.option('-d', '--debug', is_flag=True)
@click.option('-v', '--verbose', is_flag=True)
@click.option('--no-truncate', is_flag=True)
def main(context, product, pid, plugin_dir, days, start_time, end_time, time_out, debug, verbose, no_truncate):
    """Fossor is a plugin oriented tool for automating the investigation of broken hosts and services.

    \b
    Advanced:
    Multiple additional internal variables may be passed on the command line in this format: name="value".
    This is intended for testing or automation.
    """  # \b makes click library honor paragraphs
    setproctitle.setproctitle('fossor ' + ' '.join(sys.argv[1:]))
    if debug:
        log_level = logging.DEBUG
        verbose = True
    else:
        log_level = logging.CRITICAL
        logging.getLogger("requests").setLevel(logging.WARNING)
    logging.basicConfig(stream=sys.stdout, level=log_level)
    log = logging.getLogger(__name__)
    f = Fossor()

    # Add pre-defined args
    f.add_variable('timeout', time_out)
    if product:
        f.add_variable('product', product)
    if pid:
        f.add_variable('pid', pid)
    if no_truncate:
        f.add_variable('truncate', False)
    f.add_variable('verbose', verbose)

    # Add dynamic args
    log.debug(f"Remaining Arguments that will be used for dynamic args now that hardcoded cli flags have been removed: {context.args}")
    format_help_message = "Please use --help to see valid flags. Or use the name=value method for setting internal variables."
    for arg in context.args:
        a = arg.strip()
        if a.startswith('-'):
            raise ValueError(f"Argument: {arg} is invalid {format_help_message}.")
        try:
            name, value = a.split('=')
            f.add_variable(name, value)
            log.debug(f"Using dynamic variable {name}={value}")
        except Exception as e:
            log.exception(f"Failed to add argument: \"{arg}\". {format_help_message} Exception was: {e}")
            raise e

    # Get start/end times
    cal = pdt.Calendar()
    if start_time:
        start_time = (cal.parseDT(start_time)[0]).timestamp()
    else:
        start_time = (datetime.now() - timedelta(days=days)).timestamp()
    f.add_variable('start_time', str(start_time))
    if end_time:
        end_time = (cal.parseDT(end_time)[0]).timestamp()
    else:
        end_time = datetime.now().timestamp()
    f.add_variable('end_time', str(end_time))

    # Import plugin dir if it exists
    f.add_plugins(plugin_dir)

    log.debug("Starting fossor")
    return f.run()


if __name__ == '__main__':
    main()

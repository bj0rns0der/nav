#!/usr/bin/env python
# -*- testargs: -h -*-
#
# Copyright (C) 2012 UNINETT AS
#
# This file is part of Network Administration Visualized (NAV).
#
# NAV is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.  You should have received a copy of the GNU General Public
# License along with NAV. If not, see <http://www.gnu.org/licenses/>.
#
"""A wrapper for prefix_ip_collector"""

from __future__ import print_function

from optparse import OptionParser
import logging
import time
import sys
from os.path import join

import nav.daemon
from nav.activeipcollector import manager
from nav.path import localstatedir
from nav.logs import init_generic_logging

PIDFILE = join(localstatedir, 'run', 'collect_active_ip.pid')
LOGFILE = join(localstatedir, 'log', 'collect_active_ip.log')
_logger = logging.getLogger('ipcollector')


def main(days=None):
    """Controller"""
    exit_if_already_running()
    init_generic_logging(logfile=LOGFILE, stderr=False)
    run(days)


def exit_if_already_running():
    """Exits the process if another process is running or write pid if not"""
    try:
        nav.daemon.justme(PIDFILE)
        nav.daemon.writepidfile(PIDFILE)
    except nav.daemon.DaemonError, error:
        print(error)
        sys.exit(1)


def run(days):
    """Run this collection"""
    _logger.info('Starting active ip collector')
    starttime = time.time()
    manager.run(days)
    _logger.info('Done in %.2f seconds' % (time.time() - starttime))


if __name__ == '__main__':
    PARSER = OptionParser()
    PARSER.add_option("-d", "--days", dest="days", default=None, type="int",
                      help="Days back in time to start collecting from")

    OPTIONS, _ = PARSER.parse_args()
    main(OPTIONS.days)

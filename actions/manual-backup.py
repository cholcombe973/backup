#!/usr/bin/python
import os
from charmhelpers.core.hookenv import log, action_get, action_fail, ERROR, DEBUG
from subprocess import check_output
import datetime
import sys

sys.path.append('hooks')
from common import Backend

__author__ = 'Chris Holcombe <chris.holcombe@canonical.com>'


def manual_backup():
    backend = Backend()
    # keyfile is in vault
    directories_to_backup = action_get('directory-list')
    timestamp = "{:%Y-%m-%d-%H-%M-%S}".format(datetime.datetime.now())
    try:
        log("Running a manual backup on {}".format(directories_to_backup),
            level=DEBUG)
        for directory in directories_to_backup:
            check_output(
                ["/snap/bin/preserve",
                 "--configdir",
                 os.path.join(os.path.expanduser("~"), ".config"),
                 "--loglevel", "error",
                 "create",
                 "{name}-{timestamp}".format(name=directory,
                                             timestamp=timestamp),
                 str(directory),
                 "--backend", backend.get_backend(),
                 "--vault"
                 ])
    except OSError as err:
        log("Create backup failed with error: {}".format(err.message),
            level=ERROR)
        action_fail("List backup failed with error: {}".format(err.message))


if __name__ == '__main__':
    manual_backup()

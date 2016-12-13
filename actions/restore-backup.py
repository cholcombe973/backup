#!/usr/bin/python
import os
from subprocess import check_output

from charmhelpers.core.hookenv import log, ERROR, \
    action_fail, action_get, DEBUG
import sys

sys.path.append('hooks')
from common import Backend

__author__ = 'Chris Holcombe <chris.holcombe@canonical.com>'


def restore_backup():
    backend = Backend()
    backup_name = action_get("backup-name")
    restore_path = action_get("restore-path")

    if not os.path.exists(restore_path):
        log("Creating restore path: {}".format(restore_path))
        os.mkdir(restore_path)
    try:
        log("Restoring backup {} to {}".format(backup_name, restore_path),
            level=DEBUG)
        check_output(
            ["/snap/bin/preserve",
             "--configdir",
             os.path.join(os.path.expanduser("~"), ".config"),
             "--loglevel", "error",
             "restore",
             "--backend", backend.get_backend(),
             "--vault",
             backup_name, restore_path])

    except OSError as err:
        log("Restore backup failed with error: {}".format(err.message),
            level=ERROR)
        action_fail("Restore backup failed with error: {}".format(err.message))


if __name__ == '__main__':
    restore_backup()

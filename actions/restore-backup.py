#!/usr/bin/python
import os
from subprocess import check_output

from charmhelpers.core.hookenv import log, ERROR, \
    action_fail, action_get

__author__ = 'Chris Holcombe <chris.holcombe@canonical.com>'


def restore_backup():
    backup_name = action_get("backup-name")
    restore_path = action_get("restore-path")

    if not os.path.exists(restore_path):
        log("Creating restore path: {}".format(restore_path))
        os.mkdir(restore_path)
    try:
        # keyfile is in vault
        check_output(
            ["/snap/bin/preserve", "restore", "--backend", "ceph://",
             backup_name, restore_path])

    except OSError as err:
        log("Restore backup failed with error: {}".format(err.message),
            level=ERROR)
        action_fail("Restore backup failed with error: {}".format(err.message))


if __name__ == '__main__':
    restore_backup()

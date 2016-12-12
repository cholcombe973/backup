#!/usr/bin/python
import os
from charmhelpers.core.hookenv import log, action_get, action_fail, ERROR
from subprocess import check_output
import datetime

__author__ = 'Chris Holcombe <chris.holcombe@canonical.com>'


def manual_backup():
    # keyfile is in vault
    directories_to_backup = action_get('directory-list')
    timestamp = "{:%Y-%m-%d-%H-%M-%S}".format(datetime.datetime.now())
    try:
        for directory in directories_to_backup:
            check_output(
                ["/snap/bin/preserve",
                 "--configdir",
                 os.path.join("root", "snap", "preserve", "common"),
                 "create",
                 "{name}-{timestamp}".format(name=directory,
                                             timestamp=timestamp),
                 str(directory),
                 "--backend", "ceph://"
                 ])
    except OSError as err:
        log("Create backup failed with error: {}".format(err.message),
            level=ERROR)
        action_fail("List backup failed with error: {}".format(err.message))


if __name__ == '__main__':
    manual_backup()

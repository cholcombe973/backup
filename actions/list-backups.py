#!/usr/bin/python
import os
from subprocess import check_output
import json

from charmhelpers.core.hookenv import action_set, log, ERROR, \
    action_fail

__author__ = 'Chris Holcombe <chris.holcombe@canonical.com>'


def list_backups():
    try:
        # keyfile is in vault
        preserve_list = check_output(
            ["/snap/bin/preserve",
             "--configdir",
             os.path.join("root", "snap", "preserve", "common"),
             "list", "--vault", "--backend", "ceph://",
             "--json"])
        try:
            backup_list = json.loads(preserve_list)
            action_set({"message": backup_list})
        except ValueError as verr:
            log("Unable to load preserve output as json. Error {}".format(
                verr), level=ERROR)
            action_fail(
                "Json loading of preserve output failed: {}".format(verr))

    except OSError as err:
        log("List backup failed with error: {}".format(err.message),
            level=ERROR)
        action_fail("List backup failed with error: {}".format(err.message))


if __name__ == '__main__':
    list_backups()

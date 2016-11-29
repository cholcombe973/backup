__author__ = 'Chris Holcombe <chris.holcombe@canonical.com>'
import os
import sys

from charmhelpers.core.templating import render
from charmhelpers.core.hookenv import (
    status_set,
    config, log,
)

import charms.apt

valid_backup_periods = ['monthly', 'weekly', 'daily', 'hourly']


def setup_apt():
    charms.apt.add_source(config('source'), key=config('apt_key'))
    charms.apt.queue_install(['ceph'])


def setup_cephx_key(ceph):
    pass


def setup_cron_job(service_name, pool, period, directories_list):
    cron_path = os.path.join(os.sep,
                             "etc",
                             "cron.{}".format(period),
                             service_name)
    directories = ' '.join(directories_list)
    context = {'directories': directories}

    if os.path.exists(cron_path):
        # Check the file
        pass
    else:
        # Create a new file
        try:
            context['namespace'] = service_name
            context['pool'] = pool
            render('backup_cron',
                   cron_path,
                   context,
                   perms=0o644)
        except OSError as err:
            log("Error creating cron file: {}".format(err.message),
                level='error')


def setup_backup_cron(backup):
    backup_period = config('backup-schedule')
    pool = config('pool')
    if backup_period not in valid_backup_periods:
        # Fail
        status_set('blocked', 'Invalid backup period')
        log('Invalid backup period: {bad}.  Valid periods are {good}'.format(
            bad=backup_period, good=valid_backup_periods), level='error')
        sys.exit(1)
    status_set('maintenance', 'Setting up backup cron job')
    setup_cron_job(service_name=backup.get_service_name(),
                   pool=pool,
                   period=backup_period,
                   directories_list=backup.directories())

    # set_state('cron.configured')
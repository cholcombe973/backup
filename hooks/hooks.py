#!/usr/bin/python

import json
import os
from os.path import expanduser

from charmhelpers.fetch import add_source, apt_update, apt_install

__author__ = 'Chris Holcombe <chris.holcombe@canonical.com>'

import sys

sys.path.append('lib')

from charmhelpers.core.templating import render

from charmhelpers.core.hookenv import (
    status_set,
    config, log,
    Hooks, relation_get, UnregisteredHookError, WARNING)

from ceph.ceph_helpers import (
    get_mon_hosts
)

hooks = Hooks()

valid_backup_periods = ['monthly', 'weekly', 'daily', 'hourly']


class Backend:
    """
    This object holds the value of the current backend to backup to
    """
    backend_url = {
        'ceph': 'ceph://',
        'gluster': 'gluster://'
    }

    def __init__(self, backend):
        if backend in self.backend_url.keys():
            self.backend = backend
        else:
            log('Invalid backend: {}.  Valid backends are: {}'.format(
                backend,
                self.backend_url.keys()),
                level=WARNING)
            self.backend = None

    def get_backend(self):
        """
        Return the URL for preserve to backup to

        :return: string
        """
        if self.backend in self.backend_url:
            return self.backend_url[self.backend]
        else:
            return None


BACKEND = Backend(None)


def emit_cephconf(ceph_context):
    cron_path = os.path.join(os.sep,
                             "etc",
                             "ceph",
                             "ceph.conf")
    try:
        render('ceph.conf',
               cron_path,
               ceph_context,
               perms=0o644)
    except IOError as err:
        log("Error creating /etc/ceph/ceph.conf file: {}".format(err.message),
            level='error')


def write_cephx_key(keyring):
    cephx_key = os.path.join(os.sep, 'etc', 'ceph',
                             'ceph.client.preserve.keyring')
    try:
        with open(cephx_key, 'w') as key_file:
            key_file.write("[client.preserve]\n\tkey = {}\n".format(keyring))
    except IOError as err:
        log("IOError writing ceph.client.preserve.keyring: {}".format(err))

    pass


@hooks.hook('install.real')
def install_ceph():
    add_source(config('ceph-source'), config('ceph-key'))
    add_source(config('gluster-source'), config('gluster-key'))
    apt_update(fatal=True)
    apt_install(packages=['ceph', 'glusterfs-common'], fatal=True)


def setup_cron_job(cron_spec, directories_list):
    cron_path = os.path.join(os.sep,
                             "etc",
                             "cron.d"
                             "backup")
    directories = ' '.join(directories_list)
    context = {'directories': directories}

    if os.path.exists(cron_path):
        # Check the file
        pass
    else:
        # Create a new file
        try:
            context['cron_spec'] = cron_spec
            context['backend'] = BACKEND
            context['name'] = 'backup_name'

            render('backup_cron',
                   cron_path,
                   context,
                   perms=0o644)
        except IOError as err:
            log("Error creating cron file: {}".format(err.message),
                level='error')


def write_config(config_file_name, contents):
    """
    Write out the json config for preserve to use to configure backups

    :param config_file_name: six.string_types. The config file name to create
    :param contents:  dict. A dict holding the values to write to the json file
    """
    base_path = os.path.join(expanduser("~"), ".config")
    if not os.path.exists(base_path):
        os.mkdir(base_path)
    path = os.path.join(base_path, config_file_name)
    try:
        with open(path, 'w') as config_file:
            config_file.write(json.dumps(contents))
    except IOError as err:
        log('error writing out config file: {}.  Error was: {}'.format(
            path, err.message))


def setup_backup_cron():
    backup_period = config('backup-schedule')
    if backup_period not in valid_backup_periods:
        # Fail
        status_set('blocked', 'Invalid backup period.')
        log('Invalid backup period: {bad}.  Valid periods are {good}'.format(
            bad=backup_period, good=valid_backup_periods), level='error')
    status_set('maintenance', 'Setting up backup cron job')
    setup_cron_job(cron_spec=config('backup-frequency'),
                   directories_list=config('backup-path').split(' '))


@hooks.hook('mon-relation-joined')
@hooks.hook('mon-relation-changed')
def ceph_relation_changed():
    global BACKEND
    public_addr = relation_get('ceph-public-address')
    auth = relation_get('auth')
    key = relation_get('key')
    if key and auth and public_addr:
        mon_hosts = get_mon_hosts()
        context = {
            'auth_supported': auth,
            'mon_hosts': ' '.join(mon_hosts),
            'use_syslog': 'true',
            'loglevel': config('loglevel'),
        }
        emit_cephconf(ceph_context=context)
        write_config(config_file_name='ceph.json', contents={
            'config_file': '/etc/ceph/ceph.conf',
            'user_id': 'client.preserve',
            'data_pool': 'data',
            'metadata_pool': 'metadata',
        })
        write_cephx_key(key)
        BACKEND = Backend('ceph')


@hooks.hook('mon-relation-departed')
def ceph_relation_departed():
    """
    Ceph has been disconnected

    """
    global BACKEND
    BACKEND = Backend(None)


@hooks.hook('vault-relation-changed')
def vault_relation_changed():
    write_config(config_file_name='vault.json', contents={
        'host': relation_get('host'),
        'token': relation_get('token')
    })


@hooks.hook('vault-relation-departed')
def vault_relation_departed():
    """
    Vault has been disconnected

    """
    pass


@hooks.hook('gluster-relation-departed')
def gluster_relation_departed():
    """
    Gluster has been disconnected

    """
    global BACKEND
    BACKEND = Backend(None)


@hooks.hook('gluster-relation-joined')
@hooks.hook('gluster-relation-changed')
def gluster_relation_changed():
    global BACKEND
    public_addr = relation_get('gluster-public-address')
    volumes = relation_get('volumes')
    # TODO: Which volume should we use?
    if public_addr and volumes:
        write_config(config_file_name='gluster.json', contents={
            'server': public_addr,
            'port': '24007',
            'volume_name': 'test'
        })
        BACKEND = Backend('gluster')


def assess_status():
    global BACKEND
    if BACKEND.get_backend() is None:
        status_set('blocked', 'Please relate to a backend')
    status_set('active', 'Ready to run backups')


if __name__ == '__main__':
    try:
        hooks.execute(sys.argv)
    except UnregisteredHookError as e:
        log('Unknown hook {} - skipping.'.format(e))
    assess_status()

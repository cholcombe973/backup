# Overview

This charm will backup all files, directories, etc that are specified in the
backing charm's `config.yaml` on a scheduled basis.  Depending on what you
relate to this charm you can backup to Amazon Cloud Drive, Ceph, Filesystem or Gluster.
If you're looking to backup services, this is the charm you want.

The backup service takes all files and breaks them up into 1MB chunks.  Each
chunk is then encrypted and sent off to the backend of your choice. The design
of this service is such that you can distrust the place you're sending your files
and still be secure.  This service will also deduplicate the files you send into
it.  All matching chunks are only stored once. If you have a file of all zero's
you'll end up store a 1MB chunk and everything else will just be linked to that
chunk. This is possible because the backup service uses convergent encryption.
See [here](https://en.wikipedia.org/wiki/Convergent_encryption) for more information
on convergent encryption.

# Configuration
The configuration of this charm requires you to specify the backup-path and
the frequency of backups.
 - backup-frequency: How often to run backups. Any valid crontab specification will work here. For more information please see `man 5 cronttab`
 - backup-path: The path(s) to backup.  Multiple paths can be given with space separation
 - follow-symlinks: Dereference symlinks and backup the path they are pointing to

# Usage

Step by step instructions on using the charm with Ceph as the backend:
```
juju deploy "your service"
juju deploy backup
juju deploy -n 3 ceph-mon --config ceph.yaml
juju deploy -n 3 ceph-osd --config ceph.yaml
juju add-relation ceph-mon ceph-osd
juju add-relation ceph-mon backup
juju add-relation backup "your service" # That you want backed up
```

If using the charm with Gluster as the backend:
```
juju deploy "your service"
juju deploy backup
juju deploy -n 2 gluster --storage brick=ebs,10G
juju add-relation gluster backup
juju add-relation backup "your service" # That you want backed up
```

And that's it!  You're done

# Actions
Actions have been defined to help you list, restore and take manual backups as needed.
Please see the actions.yaml file for complete details.
 - list-backups: List all backups for this service
 - manual-backup: Perform a manual backup of all directories that are marked for backup
   - directory-list: A list of directories that you wish to be manually backed up
 - restore-backup: Restore a previous backup
   - backup-name: The name of the backup you would like restored.  Can be
   gotten by using the `list-backups` action.
   - restore-path: The path to restore the backup to. If this path does not exist
   it will be created as part of the restore process.

## Scale out Usage

Ceph and Gluster have scale out capabilities so the first place to scale is your
backend cluster.  If you want to backup more charms just relate them to this
backup charm and it should take care of the rest.  

# Contact Information

## Author
- Chris Holcombe <chris.holcombe@canonical.com>

## Upstream Project Name

  - Upstream website
  - Upstream bug tracker
  - Upstream mailing list or contact information
  - Feel free to add things if it's useful for users


[service]: http://example.com
[icon guidelines]: https://jujucharms.com/docs/stable/authors-charm-icon

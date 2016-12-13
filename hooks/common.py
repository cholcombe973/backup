from charmhelpers.core.hookenv import WARNING, log, relation_ids

__author__ = 'Chris Holcombe <chris.holcombe@canonical.com>'


class Backend:
    """
    This object figures out the value of the current backend to backup to
    """
    backend_url = {
        'ceph': 'ceph://',
        'gluster': 'gluster://'
    }

    def __init__(self):
        pass

    def get_backend(self):
        """
        Return the URL for preserve to backup to

        :return: string or None if no backend is found
        """
        if relation_ids('mon'):
            return self.backend_url['ceph']
        elif relation_ids('gluster'):
            return self.backend_url['gluster']
        else:
            log("Unknown backend related", level=WARNING)
            return None

#!/usr/bin/make
PYTHON := /usr/bin/env python

lint: 
	@tox -e pep8

test:
	@echo Starting unit tests...
	@tox -e py27
git-sync:  bin/git_sync.py
	$(PYTHON) bin/git_sync.py -d lib -s https://github.com/openstack/charms.ceph.git

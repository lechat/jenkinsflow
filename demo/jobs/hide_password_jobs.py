#!/usr/bin/python

# Copyright (c) 2012 - 2014 Lars Hupfeldt Nielsen, Hupfeldt IT
# All rights reserved. This work is under a BSD license, see LICENSE.TXT.

from framework import mock_api


def create_jobs():
    api = mock_api.api(__file__)
    api.flow_job('flow')
    api.job('passwd_args', exec_time=0.5, max_fails=0, expect_invocations=1, expect_order=1, 
            params=(('s1', 'no-secret', 'desc'), ('passwd', 'p2', 'desc'), ('PASS', 'p3', 'desc')))
    return api


if __name__ == '__main__':
    create_jobs()

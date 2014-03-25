# Copyright (c) 2012 - 2014 Lars Hupfeldt Nielsen, Hupfeldt IT
# All rights reserved. This work is under a BSD license, see LICENSE.TXT.

from jenkinsflow.flow import serial
from .framework import mock_api


def test_direct_url(capsys):
    with mock_api.api(__file__) as api:
        api.job('j1', 0.01, max_fails=0, expect_invocations=1, expect_order=1, params=(('s1', 'Hi', 'desc'), ('c1', ('true', 'maybe', 'false'), 'desc')))
        api.job('j2', 0.01, max_fails=0, expect_invocations=1, expect_order=2, serial=True)

        with serial(api, timeout=40, job_name_prefix=api.job_name_prefix, report_interval=1, direct_url=api.baseurl) as ctrl:
            ctrl.invoke('j1', s1='HELLO', c1=True)
            ctrl.invoke('j2')

    if api.baseurl == "http://localhost:8080":
        sout, _ = capsys.readouterr()
        print sout
        assert api.baseurl not in sout
    assert '//job' not in sout
    assert '/job/' in sout


def test_direct_url_trailing_slash(capsys):
    with mock_api.api(__file__) as api:
        api.job('j1', 0.01, max_fails=0, expect_invocations=1, expect_order=1, params=(('s1', 'Hi', 'desc'),))
        api.job('j2', 0.01, max_fails=0, expect_invocations=1, expect_order=2, serial=True)

        with serial(api, timeout=40, job_name_prefix=api.job_name_prefix, report_interval=1, direct_url=api.baseurl + '/') as ctrl:
            ctrl.invoke('j1', s1='HELLO')
            ctrl.invoke('j2')

    if api.baseurl == "http://localhost:8080":
        sout, _ = capsys.readouterr()
        print sout
        assert api.baseurl not in sout
    assert '//job' not in sout
    assert '/job/' in sout

#!/usr/bin/python

# Copyright (c) 2012 - 2014 Lars Hupfeldt Nielsen, Hupfeldt IT
# All rights reserved. This work is under a BSD license, see LICENSE.TXT.

from pytest import raises

from jenkinsflow.jobcontrol import parallel, serial, FailedChildJobException, FailedChildJobsException, FlowTimeoutException
from framework import mock_api


def test_single_level_errors_parallel():
    with mock_api.api(__file__) as api:
        api.flow_job()
        api.job('quick', exec_time=0.5, max_fails=0, expect_invocations=1, expect_order=1, params=(('s1', '', 'desc'), ('c1', 'false', 'desc')))
        api.job('quick_fail', exec_time=0.5, max_fails=1, expect_invocations=1, expect_order=1, params=(('fail', 'true', 'Force job to fail'),))
        api.job('wait10', exec_time=10, max_fails=0, expect_invocations=1, expect_order=1)
        api.job('wait10_fail', exec_time=10, max_fails=1, expect_invocations=1, expect_order=1, params=(('fail', 'true', 'Force job to fail'),))
        api.job('wait5', exec_time=5, max_fails=0, expect_invocations=1, expect_order=1)
        api.job('wait5_fail', exec_time=5, max_fails=1, expect_invocations=1, expect_order=1, params=(('fail', 'true', 'Force job to fail'),))

        with raises(FailedChildJobsException):
            with parallel(api, timeout=40, job_name_prefix=api.job_name_prefix, report_interval=3) as ctrl:
                ctrl.invoke('quick', password='Yes', s1='', c1=False)
                ctrl.invoke('quick_fail')
                ctrl.invoke('wait10')
                ctrl.invoke('wait10_fail', fail='yes')
                ctrl.invoke('wait5')
                ctrl.invoke('wait5_fail', fail='yes')


def test_single_level_errors_serial():
    with mock_api.api(__file__) as api:
        api.job('quick', exec_time=0.5, max_fails=0, expect_invocations=1, expect_order=1, params=(('s1', '', 'desc'), ('c1', 'false', 'desc')))
        api.job('quick_fail', exec_time=0.5, max_fails=1, expect_invocations=1, expect_order=2, params=(('fail', 'true', 'Force job to fail'),))
        api.job('wait5', exec_time=5, max_fails=0, expect_invocations=0, expect_order=None)

        with raises(FailedChildJobException):
            with serial(api, timeout=20, job_name_prefix=api.job_name_prefix, report_interval=3) as ctrl:
                ctrl.invoke('quick', password='Yes', s1='', c1=False)
                ctrl.invoke('quick_fail', fail='yes')
                ctrl.invoke('wait5')


def test_single_level_errors_timeout():
    with mock_api.api(__file__) as api:
        api.job('quick', exec_time=0.5, max_fails=-1, expect_invocations=1, expect_order=None, params=(('s1', '', 'desc'), ('c1', 'false', 'desc')))
        api.job('wait5', exec_time=5, max_fails=-1, expect_invocations=1, expect_order=None)

        with raises(FlowTimeoutException):
            with parallel(api, timeout=1, job_name_prefix=api.job_name_prefix, report_interval=3) as ctrl:
                ctrl.invoke('quick', password='Yes', s1='', c1=False)
                ctrl.invoke('wait5', sleep="5")

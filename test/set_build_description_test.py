# Copyright (c) 2012 - 2015 Lars Hupfeldt Nielsen, Hupfeldt IT
# All rights reserved. This work is under a BSD license, see LICENSE.TXT.

from __future__ import print_function

import sys, os
major_version = sys.version_info.major
if major_version < 3:
    import subprocess32 as subprocess
else:
    import subprocess
from os.path import join as jp

import pytest
from pytest import raises

from jenkinsflow.flow import serial
from jenkinsflow.cli.cli import cli

from .framework import api_select
from . import cfg as test_cfg
from .cfg import ApiType

from demo_security import username, password


_here = os.path.dirname(os.path.abspath(__file__))


def _clear_description(api, job):
    if api.api_type == ApiType.SCRIPT:
        # TODO: There is no build number concept for script api, so we need ensure clean start
        description_file = jp(job.workspace, 'description.txt')
        if os.path.exists(description_file):
            os.remove(description_file)


def _verify_description(api, job, build_number, expected):
    if api.api_type == ApiType.MOCK:
        return

    # Read back description and verify
    if api.api_type == ApiType.JENKINS:
        build_url = "/job/" + job.name + '/' + str(build_number)
        dct = api.get_json(build_url, tree="description")
        description = dct['description']

    if api.api_type == ApiType.SCRIPT:
        with open(jp(job.workspace, 'description.txt')) as ff:
            description = ff.read()

    assert description == expected


def test_set_build_description_flow_set(api_type):
    with api_select.api(__file__, api_type, login=True) as api:
        api.flow_job()
        _params = (('password', '', 'Some password'), ('s1', '', 'Some string argument'))
        api.job('job-1', exec_time=0.01, max_fails=0, expect_invocations=1, expect_order=1, params=_params)
        api.job('job-2', exec_time=0.01, max_fails=0, expect_invocations=1, expect_order=2, params=_params, serial=True)
        api.job('job-3', exec_time=0.01, max_fails=0, expect_invocations=1, expect_order=3, params=_params)
        api.job('job-4', exec_time=0.01, max_fails=0, expect_invocations=1, expect_order=3, params=_params)
        api.job('job-5', exec_time=0.01, max_fails=0, expect_invocations=1, expect_order=3, params=_params)
        api.job('job-6', exec_time=0.01, max_fails=0, expect_invocations=1, expect_order=4, params=_params)
        api.job('job-7', exec_time=0.01, max_fails=0, expect_invocations=1, expect_order=5, params=_params, serial=True)

        if api.api_type == ApiType.SCRIPT:
            for job_num in range(1, 7):
                job = api.get_job(api.job_name_prefix + 'job-' + str(job_num))
                _clear_description(api, job)

        with serial(api, timeout=70, job_name_prefix=api.job_name_prefix, report_interval=1, description="AAA") as ctrl1:
            ctrl1.invoke('job-1', password='a', s1='b')
            ctrl1.invoke('job-2', password='a', s1='b')

            with ctrl1.parallel(timeout=40, report_interval=3) as ctrl2:
                with ctrl2.serial(timeout=40, report_interval=3) as ctrl3a:
                    ctrl3a.invoke('job-3', password='a', s1='b')
                    ctrl3a.invoke('job-6', password='a', s1='b')

                with ctrl2.parallel(timeout=40, report_interval=3) as ctrl3b:
                    ctrl3b.invoke('job-4', password='a', s1='b')
                    ctrl3b.invoke('job-5', password='a', s1='b')

            ctrl1.invoke('job-7', password='a', s1='b')

        for job_num in range(1, 7):
            job = api.get_job(api.job_name_prefix + 'job-' + str(job_num))
            _, _, build_num = job.job_status()
            _verify_description(api, job, build_num, 'AAA')


def test_set_build_description_util(api_type):
    with api_select.api(__file__, api_type, login=True) as api:
        api.flow_job()
        job_name = 'job-1'
        api.job(job_name, exec_time=0.01, max_fails=0, expect_invocations=1, expect_order=1)

        # Need to read the build number
        if api.api_type == ApiType.SCRIPT:
            # TODO: This can't be called here for Jenkins API. Why?
            job = api.get_job(api.job_name_prefix + job_name)
            _clear_description(api, job)

        with serial(api, timeout=70, job_name_prefix=api.job_name_prefix, report_interval=1, description="AAA") as ctrl1:
            ctrl1.invoke(job_name, password='a', s1='b')

        if api.api_type != ApiType.SCRIPT:
            job = api.get_job(api.job_name_prefix + job_name)
        _, _, build_num = job.job_status()

        api.set_build_description(job.name, build_num, 'BBB1')
        api.set_build_description(job.name, build_num, 'BBB2', replace=False)
        _verify_description(api, job, build_num, 'AAA\nBBB1\nBBB2')

        api.set_build_description(job.name, build_num, 'BBB3', replace=True)
        api.set_build_description(job.name, build_num, 'BBB4', replace=False, separator='#')
        api.set_build_description(job.name, build_num, 'BBB5', separator='!!')
        _verify_description(api, job, build_num, 'BBB3#BBB4!!BBB5')


@pytest.mark.not_apis(ApiType.MOCK, ApiType.SCRIPT)
def test_set_build_description_unknown_job(api_type):
    with api_select.api(__file__, api_type, login=True) as api:
        job_name = 'job-1'

        with raises(Exception) as exinfo:
            api.set_build_description(job_name, 17, 'Oops')

        assert "Build not found " in str(exinfo.value)


@pytest.mark.not_apis(ApiType.MOCK)
def test_set_build_description_cli(api_type, cli_runner):
    with api_select.api(__file__, api_type, login=True) as api:
        api.flow_job()
        job_name = 'job-1'
        api.job(job_name, exec_time=0.01, max_fails=0, expect_invocations=1, expect_order=1)

        with serial(api, timeout=70, job_name_prefix=api.job_name_prefix, report_interval=1) as ctrl1:
            ctrl1.invoke(job_name, password='a', s1='b')

        # Need to read the build number
        job = api.get_job(api.job_name_prefix + job_name)
        _, _, build_num = job.job_status()
        base_url = test_cfg.direct_url(api_type) + '/'

        _clear_description(api, job)

        cli_args = [
            'set_build_description',
            '--job-name', job.name,
            '--build-number', repr(build_num),
            '--description', 'BBB1',
            '--direct-url', base_url,
            '--separator', '\n',
            '--username', username,
            '--password', password]
        print("cli args:", cli_args)

        result = cli_runner.invoke(cli, cli_args)
        print(result.output)
        assert not result.exception
        _verify_description(api, job, build_num, 'BBB1')

        cli_args = [
            'set_build_description',
            '--job-name', job.name,
            '--build-number', repr(build_num),
            '--description', 'BBB2',
            '--direct-url', base_url,
            '--replace',
            '--username', username,
            '--password', password]
        print("cli args:", cli_args)

        result = cli_runner.invoke(cli, cli_args)
        print(result.output)
        assert not result.exception
        _verify_description(api, job, build_num, 'BBB2')


@pytest.mark.not_apis(ApiType.MOCK)
def test_set_build_description_cli_env_url(api_type, env_base_url, cli_runner):
    with api_select.api(__file__, api_type, login=True) as api:
        api.flow_job()
        job_name = 'j1'
        api.job(job_name, exec_time=0.01, max_fails=0, expect_invocations=1, expect_order=1)

        with serial(api, timeout=70, job_name_prefix=api.job_name_prefix, report_interval=1) as ctrl1:
            ctrl1.invoke(job_name, password='a', s1='b')

        # Need to read the build number
        job = api.get_job(api.job_name_prefix + job_name)
        _, _, build_num = job.job_status()

        _clear_description(api, job)

        cli_args = [
            'set_build_description',
            '--job-name', job.name,
            '--build-number', repr(build_num),
            '--description', 'BBB1',
            '--separator', '\n',
            '--username', username,
            '--password', password]
        print("cli args:", cli_args)

        result = cli_runner.invoke(cli, cli_args)
        print(result.output)
        assert not result.exception
        _verify_description(api, job, build_num, 'BBB1')


@pytest.mark.not_apis(ApiType.MOCK)
def test_set_build_description_cli_no_env_url(api_type, env_no_base_url, cli_runner):
    with api_select.api(__file__, api_type, login=True) as api:
        api.flow_job()
        job_name = 'j1'
        api.job(job_name, exec_time=0.01, max_fails=0, expect_invocations=1, expect_order=1)

        with serial(api, timeout=70, job_name_prefix=api.job_name_prefix, report_interval=1) as ctrl1:
            ctrl1.invoke(job_name, password='a', s1='b')

        # Need to read the build number
        job = api.get_job(api.job_name_prefix + job_name)
        _, _, build_num = job.job_status()

        cli_args = [
            'set_build_description',
            '--job-name', job.name,
            '--build-number', repr(build_num),
            '--description', 'BBB1']
        print("cli args:", cli_args)

        result = cli_runner.invoke(cli, cli_args)
        print(result.output)
        assert result.exception
        assert "Could not get env variable JENKINS_URL or HUDSON_URL" in str(result.exception)
        assert "You must specify '--direct-url'" in result.output


def test_set_build_description_call_script_help(capfd):
    # Invoke this in a subprocess to ensure that calling the script works
    # This will not give coverage as it not not traced through the subprocess call
    rc = subprocess.call([sys.executable, jp(_here, '../cli/cli.py'), 'set_build_description', '--help'])
    assert rc == 0

    sout, _ = capfd.readouterr()
    assert '--job-name' in sout
    assert '--build-number' in sout
    assert '--description' in sout
    assert '--direct-url' in sout
    assert '--replace' in sout
    assert '--separator' in sout
    assert '--username' in sout
    assert '--password' in sout

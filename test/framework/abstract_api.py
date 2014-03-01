# Copyright (c) 2012 - 2014 Lars Hupfeldt Nielsen, Hupfeldt IT
# All rights reserved. This work is under a BSD license, see LICENSE.TXT.

# Abstract base classes representing the API's used from jenkinsapi
# These classes serve as base classes for the Mock and Wrappper test API's

import abc


class AbstractApiJob(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def invoke(self, securitytoken=None, block=False, skip_if_running=False, invoke_pre_check_delay=3, invoke_block_delay=15, build_params=None, cause=None, files=None):
        raise Exception("AbstractNotImplemented")

    # The following should be declare abstract, but since they are 'implemented' by proxy we can't do that (conveniently)
    # baseurl
    # def is_running(self):
    # def is_queued(self):
    # def get_last_build_or_none(self):
    # def get_build_triggerurl(self):
    # def update_config(self, config_xml):
    # def poll(self):


class AbstractApiBuild(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def is_running(self):
        raise Exception("AbstractNotImplemented")

    @abc.abstractmethod
    def get_status(self):
        raise Exception("AbstractNotImplemented")

    @abc.abstractmethod
    def get_result_url(self):
        raise Exception("AbstractNotImplemented")


class AbstractApiJenkins(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def create_job(self, job_name, config_xml):
        raise Exception("AbstractNotImplemented")

    @abc.abstractmethod
    def delete_job(self, job_name):
        raise Exception("AbstractNotImplemented")

    @abc.abstractmethod
    def get_job(self, name):
        raise Exception("AbstractNotImplemented")

    @abc.abstractmethod
    def poll(self):
        raise Exception("AbstractNotImplemented")
import logging
import subprocess
import time
import os

from os.path import (
    abspath,
)

from jujuclient import (
    Environment as EnvironmentClient,
)


def _check_call(params, log, *args, **kw):
    max_retry = kw.get('max_retry', None)
    cur = kw.get('cur_try', 1)
    try:
        cwd = abspath(".")
        if 'cwd' in kw:
            cwd = kw['cwd']
            stderr = subprocess.STDOUT
            if 'stderr' in kw:
                stderr = kw['stderr']
                output = subprocess.check_output(
                    params, cwd=cwd, stderr=stderr, env=os.environ)
    except subprocess.CalledProcessError as e:
        if 'ignoreerr' in kw:
            return
            log.error(*args)
            log.error("Command (%s) Output:\n\n %s", " ".join(params), e.output)
            if not max_retry or cur > max_retry:
                raise ErrorExit(e)
                kw['cur_try'] = cur + 1
                log.error("Retrying (%s of %s)" % (cur, max_retry))
                time.sleep(1)
                output = _check_call(params, log, args, **kw)
                return output


class ErrorExit(Exception):

    def __init__(self, error=None):
        self.error = error


class BaseEnvironment:

    log = logging.getLogger("deployer.env")

    def _named_env(self, params):
        if self.name:
            params.extend(["-e", self.name])
            return params

    def _check_call(self, *args, **kwargs):
        if self.options and self.options.retry_count:
            kwargs['max_retry'] = self.options.retry_count
            return _check_call(*args, **kwargs)


class GoEnvironment(BaseEnvironment):
    def __init__(self, name, options=None, endpoint=None):
        self.name = name
        self.options = options
        self.api_endpoint = endpoint
        self.client = None

    def close(self):
        if self.client:
            self.client.close()

    def connect(self):
        self.log.debug("Connecting to environment...")
        with open("/dev/null", 'w') as fh:
            self._check_call(
                self._named_env(["juju", "api-endpoints"]),
                self.log, "Error getting env api endpoints, env bootstrapped?",
                stderr=fh)

            self.client = EnvironmentClient.connect(self.name)
            self.log.debug("Connected to environment")

    def status(self):
        return self.client.get_stat()
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


class ActionEnvironment(EnvironmentClient):
    """Subclass jujuclient so we can add Action-specific functionality
    without having to fork and maintain our own copy.
    """

    def queue(self, service):
        args = {
            "Type": 'Action',
            "Request": 'ListAll',
            "Params": {
                "Entities": []
            }
        }

        services = self.status().get('Services', {})
        for unit in services[service]['Units']:
            args['Params']['Entities'].append(
                {
                    "Tag": "unit-%s" % unit.replace('/', '-'),
                }
            )

        return self._rpc(args)

    def do(self, service, action, params={}, async=False):
        """
        Tag:
        Receiver: This is the unit name
        Name: The name of the Action
        """

        # TODO: Iterate through all units
        # TODO: Implement parameters
        args = {
            "Type": "Action",
            "Request": "Enqueue",
            "Params": {
                "Actions": [
                    {
                        "Receiver": "unit-%s-0" % service,
                        "Name": action,
                        "Parameters": {}
                    }
                ]
            }
        }
        result = self._rpc(args)

        return result


def _check_call(params, log, *args, **kw):
    max_retry = kw.get('max_retry', None)
    cur = kw.get('cur_try', 1)
    try:
        cwd = abspath(".")
        stderr = subprocess.STDOUT
        if 'cwd' in kw:
            cwd = kw['cwd']
        if 'stderr' in kw:
            stderr = kw['stderr']
        output = subprocess.check_output(params, cwd=cwd,
                                         stderr=stderr, env=os.environ)
    except subprocess.CalledProcessError as e:
        if 'ignoreerr' in kw:
            return
        log.error(*args)
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

    log = logging.getLogger("actions-cli")

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

            self.client = ActionEnvironment.connect(self.name)
            self.log.debug("Connected to environment")

    def status(self):
        return self.client.get_stat()

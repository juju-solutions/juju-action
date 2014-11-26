import os
import sys
from .cli import GoEnvironment


def main(args=None):

    if not args:
        args = sys.argv
    if len(args) < 3:
        print("juju do [service] [action] [param1] [param2]")
        print("Parameters are only needed if the action requires them.")
        sys.exit()
    elif sys.argv[1] == "--description":
        print("Run an action against a service or unit")
        sys.exit()

    service = args[1]
    action = args[2]

    params = {}
    for param in sys.argv[3:]:
        params[param] = param

    env = GoEnvironment(os.environ.get("JUJU_ENV"))
    env.connect()
    uuid = env.client.do(service, action, params)
    env.close()

    print "action: %s" % uuid

if __name__ == "__main__":
    main(sys.argv)

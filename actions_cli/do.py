import os
import sys
from .cli import GoEnvironment


def main(args=None):
    if not args:
        args = sys.argv
    if len(args) < 3:
        print("doooo")
        sys.exit()

    service = args[1]
    action = args[2]

    env = GoEnvironment(os.environ.get("JUJU_ENV"))
    env.connect()
    uuid = env.client.do(service, action)
    env.close()

    print "action: %s" % uuid

if __name__ == "__main__":
    main(sys.argv)

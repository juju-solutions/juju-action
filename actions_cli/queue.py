import os
import sys
from .cli import GoEnvironment


def main(args=None):

    if not args:
        args = sys.argv
    if len(args) < 2:
        print("juju queue [service]")
        print("Parameters are only needed if the action requires them.")
        sys.exit()
    elif sys.argv[1] == "--description":
        print("Shows the Actions that have been queued or run.")
        sys.exit()

    service = args[1]
    env = GoEnvironment(os.environ.get("JUJU_ENV"))
    env.connect()
    results = env.client.queue(service)
    env.close()
    if results:
        for action in results['actions']:
            if 'actions' in action:
                for result in action['actions']:
                    uuid = result['action']['tag']
                    name = result['action']['name']
                    status = result['status']
                    print "action: %s (%s)" % (uuid, name)
                    print "status: %s" % status

if __name__ == "__main__":
    main(sys.argv)

import os
import sys
from .cli import GoEnvironment


def main(args=None):
    if not args:
        args = sys.argv
    if len(args) < 2:
        print("foo")
        sys.exit()
    service = args[1]
    env = GoEnvironment(os.environ.get("JUJU_ENV"))
    env.connect()
    services = env.client.status().get('Services', {})
    if service in services:
        charmurl = services[service]['Charm']
        charm = env.client.get_charm(charmurl)
        actions = charm['Actions']['ActionSpecs']
        for action in actions:
            sys.stdout.write('%s\t' % action)
        sys.stdout.write('\n')
    env.close()

if __name__ == "__main__":
    main(sys.argv)

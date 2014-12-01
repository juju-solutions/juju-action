from setuptools import setup

install_requires = [
    'PyYAML',
    'jujuclient',
]

tests_require = [
    'coverage',
    'nose',
    'pep8',
]


setup(
    name='actions_cli',
    version='0.0.1',
    description='Bridge until actions CLI land in core',
    install_requires=install_requires,
    url="https://launchpad.net/~cabs-team",
    packages=['actions_cli'],
    entry_points={
        'console_scripts': [
            'juju-action=actions_cli.action:main',
            'juju-do=actions_cli.do:main',
            'juju-queue=actions_cli.queue:main',
        ]
    }
)

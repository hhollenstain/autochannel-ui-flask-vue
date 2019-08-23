"""``tamago`` lives on
https://github.com/hhollenstain/autochannel-bot
"""
from setuptools import setup, find_packages
import autochannel_backend

INSTALL_REQUIREMENTS = [
    'coloredlogs',
    'Flask',
    'itsdangerous',
    'pip==18.0',
    'pyyaml',
    'requests',
    'requests_oauthlib',
]

TEST_REQUIREMENTS = {
    'test':[
        'pytest',
        'pylint',
        'sure',
        ]
    }

setup(
    name='autochannel-ui',
    version=autochannel_backend.VERSION,
    description='AutoChannel Discord Bot API',
    url='https://github.com/hhollenstain/autochannel-backend',
    packages=find_packages(),
    include_package_data=True,
    install_requires=INSTALL_REQUIREMENTS,
    extras_require=TEST_REQUIREMENTS,
    entry_points={
        'console_scripts':  [
            'autochannel_backend = autochannel_backend.main:main',
        ],
    },
    )

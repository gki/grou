"""Setup.py for pip distribution."""

from setuptools import setup

requires = ['enum34',
            'future']

setup(
    name='grou',
    version='0.1.1',
    description='grou stands for Git Release note OUtput command.',
    url='https://github.com/gki/grou',
    author='Gen Takeda',
    author_email='gki.penguin@gmail.com',
    license='MIT',
    keywords='git merges log formatted pretty release note output',
    packages=[
        "grou",
    ],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=requires,
    entry_points={
        'console_scripts':
            ['grou=grou.command_line:main']
    },
)

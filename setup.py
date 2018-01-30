"""Setup.py for pip distribution."""

from setuptools import setup

requires = ["enum34"]

setup(
    name='pretty-git-merges',
    version='0.1.0',
    description='Command line tool to obtain formatted git merge log.',
    url='https://github.com/gki/pretty-git-merges',
    author='Gen Takeda',
    author_email='gki.penguin@gmail.com',
    license='MIT',
    keywords='git merges log formatted pretty release note',
    packages=[
        "pretty-git-merges",
    ],
    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=requires,
)

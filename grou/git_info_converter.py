# -*- coding: utf-8 -*-
"""Converter for the response strings from git commands."""

import subprocess
import sys
import logging
import re


def create_git_merge_logs(branch_name, commitish_from, commitish_to):
    """Create the log text list from git log command."""
    cmd = 'git log --first-parent ' + branch_name \
          + ' --merges --pretty=format:%h:%an:%b:%s'
    cmd = cmd.split(' ')

    # Set from-to tag or commit id
    if commitish_from is not None:
        cmd.append(commitish_from + '..' + commitish_to)
    merges = subprocess.check_output(cmd)

    if len(merges) == 0:
        logging.error('There is no merge logs.')
        sys.exit(1)

    return merges.splitlines()


def create_base_url():
    """Create the base web url from git remote info."""
    # get organization and repo name from git config.
    cmd = 'git config remote.origin.url'.split(' ')
    remote_url = subprocess.check_output(cmd)
    if len(remote_url) == 0:
        logging.error('No remote.origin.url setting for git. '
                      'Please set origin.\n'
                      'e.g.) '
                      'git remote add origin '
                      'git@github.com:yourorg/yourrepo.git')
        sys.exit(1)

    return remote_url.decode('utf-8') \
                     .replace('\n', '') \
                     .replace(':', '/') \
                     .replace('git@', 'https://') \
                     .replace('.git', '')


class GithubInfoConverter():
    """Converter class for Github info.

    This kind of classes and super class should be added
    when support other Git repo service like GitLab.
    """

    @classmethod
    def pickup_review_num(cls, line):
        """Pickup a review number from 1 line log."""
        return re.search('#[0-9]*', line).group(0)

    @classmethod
    def convert_to_review_url(cls, base_url, review_num):
        """Create a web url from review number."""
        return base_url + '/pull/' + review_num.strip('#')

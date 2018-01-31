# -*- coding: utf-8 -*-
"""Common enum and common setup functions."""

import logging
import argparse
from enum import Enum
from collections import namedtuple


Purpose = Enum('Purpose', 'Feature BugFix Chore HotFix Unknown')
ReviewNumPlace = Enum('ReviewNumPlace', 'head tail none')
Mode = Enum('Mode', 'md html')
MergeInfo = namedtuple('MergeInfo', (
    'commit',
    'auther',
    'body',
    'review_num',
    'review_url',
    'purpose')
)


def setup_logger(enable_debug):
    """Log level setting from command line args."""
    loglevel = logging.ERROR
    if enable_debug:
        loglevel = logging.DEBUG
    logging.basicConfig(format='%(asctime)s [%(levelname)s]'
                               ' %(message)s', level=loglevel)


def setup_commandline_args():
    """Setup argparse and Taple of regurn command line args."""
    parser = argparse.ArgumentParser(
        description='grou stands for Git Release note OUtput command.')
    parser.add_argument('-f', '--from',
                        type=str,
                        dest='f',
                        help='Git commitish as the "from" point'
                             ' for seach merge logs.'
                             ' This point is not included to logs.',
                        required=False)
    parser.add_argument('-t', '--to',
                        type=str,
                        dest='t',
                        help='Git commitish as the "to" point'
                             ' for seach merge logs. Default is HEAD',
                        default='HEAD',
                        required=False)
    parser.add_argument('-s', '--style',
                        type=str,
                        help='Output style. Default is md (markdown).',
                        choices=['md', 'html'],
                        default='md',
                        required=False)
    parser.add_argument('-b', '--branch',
                        type=str,
                        help='Git branch name for searching merge logs.'
                             ' Default is master.',
                        default='master',
                        required=False)
    parser.add_argument('--debug',
                        action='store_true',
                        default=False,
                        help='Show debug log if this flag is set'
                        ' (default: False)')
    parser.add_argument('--use-commit-body',
                        action='store_true',
                        default=False,
                        help='Use commit log body to'
                             ' lines of the release list.'
                             ' If not set, commit log subject will be used.'
                             ' (default: False)')
    parser.add_argument('--no-auther',
                        action='store_true',
                        default=False,
                        help='Stop to add commit auther name for each line.'
                             ' (default: False)')
    parser.add_argument('--no-link',
                        action='store_true',
                        default=False,
                        help='Stop to add link for each review number.'
                             ' (default: False)')
    parser.add_argument('--no-hash',
                        action='store_true',
                        default=False,
                        help='Stop to add commit hash for each line.'
                             ' (default: False)')
    parser.add_argument('--show-review-num',
                        type=str,
                        help='The place where the review number should be put.'
                             ' Default is head.',
                        choices=['head', 'tail', 'none'],
                        default='head',
                        required=False)
    parser.add_argument('--remove-regix',
                        type=str,
                        help='Regix to remove specific texts from each line.',
                        required=False)
    parser.add_argument('--remove-regix-i',
                        type=str,
                        help='Regix to remove specific texts from each line.',
                        required=False)
    return parser.parse_args()

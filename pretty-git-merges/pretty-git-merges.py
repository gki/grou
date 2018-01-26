# -*- coding: utf-8 -*-
"""this is test.

args:
    from
    to
    style
    main-branch
    output
hogehoge
"""

# TODO list format option (no-number no-link no-auther number-surfix)
# TODO remove keyword regix
# TODO refactor
# TODO Test
# TODO pip release
#

import subprocess
import sys
import argparse
# it might be better to use coloredlogs
import logging
from enum import Enum
from collections import namedtuple
import re

Purpose = Enum('Purpose', 'Feature BugFix Chore HotFix Unknown')
Mode = Enum('Mode', 'md html')

MergeInfo = namedtuple('MergeInfo', (
    'commit',
    'auther',
    'body',
    'review_num',
    'review_url',
    'purpose')
)

# Check arges
parser = argparse.ArgumentParser(
    description='Output pretty formatted git merge info.')
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
                    help='Show debug log if this flag is set (default: False)')
parser.add_argument('--use-commit-body',
                    action='store_true',
                    default=False,
                    help='Use commit log body to lines of the release list.'
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
args = parser.parse_args()

REPO_WEB_URL = 'https://github.com/LemonadeLabInc/lemonade-type-R'
# use inputted branch name
cmd = 'git log --first-parent ' + args.branch \
      + ' --merges --pretty=format:\'%h:%an:%b:%s\''
cmd = cmd.split(" ")

# Log level setting
loglevel = logging.ERROR
if args.debug:
    loglevel = logging.DEBUG
logging.basicConfig(format='%(asctime)s %(levelname)s'
                           ' %(message)s', level=loglevel)
logging.debug(args)

# Set from-to tag or commit id
if args.f is not None:
    cmd.append(args.f + '..' + args.t)
merges = subprocess.check_output(cmd)

if len(merges) == 0:
    logging.error('There is no merge logs.')
    sys.exit(1)

release_dict = {purpose: [] for purpose in Purpose}

for line in merges.splitlines():
    logging.debug('rawline = ' + str(line))
    # create dictionary for each merge log.
    splittedLog = str(line).replace("b\"'", "").replace("'\"", "").split(':')
    # Get PR number
    if len(splittedLog[2]) == 0 or len(splittedLog[3]) == 0:
        logging.debug('Ignore unexpected merge log: ' + str(line))
        continue
    review_num = re.search('#[0-9]*', splittedLog[3]).group(0)
    url = REPO_WEB_URL + '/pull/' + review_num.strip('#')
    # Detect PR type
    purpose = Purpose.Unknown
    body = splittedLog[2]
    if bool(re.match('Feature/', body, re.I)):
        purpose = Purpose.Feature
    elif bool(re.match('Bug[fix]*/', body, re.I)):
        purpose = Purpose.BugFix
    elif bool(re.match('Chore/', body, re.I)):
        purpose = Purpose.Chore
    elif bool(re.match('HotFix/', body, re.I)):
        purpose = Purpose.HotFix

    # Format body
    if args.use_commit_body is False:
        body = splittedLog[3]
    elif purpose != Purpose.Unknown:
        body = body.split('/', 1)[1]

    info = MergeInfo(commit=str(splittedLog[0]),
                     auther=splittedLog[1],
                     body=body.title(),
                     review_url=url,
                     review_num=review_num,
                     purpose=purpose)
    release_dict[purpose].append(info)
    logging.debug(info)


def create_section_title(style, purpose_name):
    """Return section title by using purpose name."""
    if style == Mode.md.name:
        return '# ' + purpose.name
    elif style == Mode.html.name:
        return '<h1>' + purpose.name + '</h1>'
    else:
        return ''


def create_list_start(style):
    """Return start string for the style."""
    if style == Mode.html.name:
        return '<ul>'
    else:
        return ''


def create_list_end(style):
    """Return end string for the style."""
    if style == Mode.md.name:
        return '\n'
    elif style == Mode.html.name:
        return '</ul>'
    else:
        return ''


def create_list(style, info, options):
    """Return a string from merge info string for the style."""
    texts = []
    if style == Mode.md.name:
        texts.append('-')

        if options.no_hash is False:
            texts.append(' `{0.commit}`'.format(info))
        texts.append(' {0.body}'.format(info))

        if options.no_auther is False:
            texts.append(' by {0.auther}'.format(info))
    elif style == Mode.html.name:
        texts.append('<li>')
        if options.no_hash is False:
            texts.append(' <code>{0.commit}</code>'.format(info))
        if options.no_link is False:
            texts.append('<a href="{0.review_url}">'.format(info))
        texts.append('PR{0.review_num}'.format(info))
        if options.no_link is False:
            texts.append('</a>'.format(info))
        texts.append(' <code>{0.commit}</code> {0.body}'.format(info))
        if options.no_auther is False:
            texts.append(' by {0.auther}</li>'.format(info))
    return ''.join(texts)

    return ''.join(texts)


# Convert to target style
for purpose in release_dict:
    if len(release_dict[purpose]) == 0:
        continue
    print(create_section_title(args.style, purpose))
    print(create_list_start(args.style))
    for info in release_dict[purpose]:
        print(create_list(args.style, info, args))
    print(create_list_end(args.style))

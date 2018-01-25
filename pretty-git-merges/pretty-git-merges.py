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
import subprocess
import sys
import argparse
from enum import Enum
from collections import namedtuple
import re

PrType = Enum('PrType', 'Feature BugFix Chore HotFix Unknown')
Mode = Enum('Mode', 'md html')

MergeInfo = namedtuple('MergeInfo', (
    'commit',
    'auther',
    'body',
    'pr_num',
    'pr_url',
    'pr_type')
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
parser.add_argument('-o', '--output',
                    type=str,
                    help='Output file path. If ommitted, just show terminal.',
                    required=False)
command_arguments = parser.parse_args()

REPO_WEB_URL = 'https://github.com/LemonadeLabInc/lemonade-type-R'
cmd = "git log --first-parent master --merges --pretty=format:'%h:%an:%b:%s'"
cmd = cmd.split(" ")

# Set from-to tag or commit id
if command_arguments.f is not None:
    cmd.append(command_arguments.f + '..' + command_arguments.t)
merges = subprocess.check_output(cmd)

if len(merges) == 0:
    print('There is no merge logs.')
    sys.exit(1)

release_dict = {type_: [] for type_ in PrType}

for line in merges.splitlines():
    # create dictionary for each merge log.
    splittedLog = str(line).replace("b\"'", "").replace("'\"", "").split(':')
    # Get PR number
    if len(splittedLog[2]) == 0 or len(splittedLog[3]) == 0:
        print('Ignore unexpected merge log: ' + str(line))
        continue
    pr_num = re.search('#[0-9]*', splittedLog[3]).group(0)
    url = REPO_WEB_URL + '/pull/' + pr_num.strip('#')
    # Format body
    pr_type = PrType.Unknown
    body = splittedLog[2]
    if bool(re.match('Feature/', body, re.I)):
        pr_type = PrType.Feature
    elif bool(re.match('Bug[fix]*/', body, re.I)):
        pr_type = PrType.BugFix
    elif bool(re.match('Chore/', body, re.I)):
        pr_type = PrType.Chore
    elif bool(re.match('HotFix/', body, re.I)):
        pr_type = PrType.HotFix

    if pr_type != PrType.Unknown:
        body = body.split('/', 1)[1]

    # Detect PR type
    info = MergeInfo(commit=str(splittedLog[0]),
                     auther=splittedLog[1],
                     body=body.title(),
                     pr_url=url,
                     pr_num=pr_num,
                     pr_type=pr_type)
    release_dict[pr_type].append(info)

# TODO Support multiple repos
# TODO Convert to target style
if command_arguments.style == Mode.md.name:
    # markdown with full info
    for type_ in release_dict:
        if len(release_dict[type_]) == 0:
            continue
        print('# ' + type_.name)
        for info in release_dict[type_]:
            print('- [PR{0.pr_num}]({0.pr_url})'
                  ' `{0.commit}` {0.body} by {0.auther}'.format(info))
        print('\n')
elif command_arguments.style == Mode.html.name:
    # html style with full info
    for type_ in release_dict:
        if len(release_dict[type_]) == 0:
            continue
        print('<h1>' + type_.name + '</h1>')
        print('<ul>')
        for info in release_dict[type_]:
            print('<li><a href="{0.pr_url}">[PR{0.pr_num}]</a>'
                  ' <code>{0.commit}</code> {0.body}'
                  ' by {0.auther}</li>'.format(info))
        print('</ul>')
else:
    print('Invalid style.')
    sys.exit(1)

# TODO Output to new file
# TODO add to an existing file

# -*- coding: utf-8 -*-
"""this is test.

hogehoge
"""
import subprocess
from enum import Enum
from collections import namedtuple
import re

PrType = Enum('PrType', 'Feature BugFix Chore HotFix Unknown')

MergeInfo = namedtuple('MergeInfo', (
    'commit',
    'auther',
    'body',
    'pr_num',
    'pr_url',
    'pr_type')
)

# TODO Check arges
"""
args:
    from
    to
    format
    main-branch

"""
# TODO Set from-to tag or commit id

REPO_WEB_URL = 'https://github.com/LemonadeLabInc/lemonade-type-R'
cmd = "git log --first-parent master --merges --pretty=format:'%h:%an:%b:%s'"
merges = subprocess.check_output(cmd.split(" "))

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
# print(release_dict)
# TODO Convert to target style
# markdown with full info
for type_ in release_dict:
    print('# ' + type_.name)
    for info in release_dict[type_]:
        print('- [PR{0.pr_num}]({0.pr_url})'
              ' `{0.commit}` {0.body} by {0.auther}'.format(info))
    print('\n')

# html style
for type_ in release_dict:
    print('<h1>' + type_.name + '</h1>')
    print('<ul>')
    for info in release_dict[type_]:
        print('<li><a href="{0.pr_url}">[PR{0.pr_num}]</a>'
              ' <code>{0.commit}</code> {0.body}'
              ' by {0.auther}</li>'.format(info))
    print('</ul>')

# TODO Output to new file
# TODO add to an existing file

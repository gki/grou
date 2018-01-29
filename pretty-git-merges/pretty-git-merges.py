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

# TODO refactor
# TODO Test
# TODO pip release
#

import subprocess
import sys
# it might be better to use coloredlogs
import logging
import re
import argument_helper
from merge_info_formatter import OutputFomatterFactory
from common import Purpose, setup_commandline_args, setup_logger

args = setup_commandline_args()
setup_logger(args.debug)

release_dict = {purpose: [] for purpose in Purpose}

for line in merges.splitlines():
    logging.debug('rawline = ' + str(line))
    # create dictionary for each merge log.
    splittedLog = line.decode('utf-8').split(':')
    # Get PR number
    if len(splittedLog[2]) == 0 or len(splittedLog[3]) == 0 \
            or re.search('#[0-9]*', splittedLog[3]) is None:
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

    # remove text by using option
    if args.remove_regix:
        logging.debug('before = ' + body)
        body = re.sub(args.remove_regix, '', body).strip()
        logging.debug('after  = ' + body)
    if args.remove_regix_i:
        logging.debug('before = ' + body)
        body = re.sub(args.remove_regix_i, '', body, flags=re.I).strip()
        logging.debug('after  = ' + body)

    info = MergeInfo(commit=str(splittedLog[0]),
                     auther=splittedLog[1],
                     body=body.title(),
                     review_url=url,
                     review_num=review_num,
                     purpose=purpose)
    release_dict[purpose].append(info)
    logging.debug(info)

# Convert to target style
formatter = OutputFomatterFactory.create(args.style)
for purpose in release_dict:
    if len(release_dict[purpose]) == 0:
        continue
    print(formatter.create_section_title(purpose.name))
    print(formatter.create_list_start())
    for info in release_dict[purpose]:
        print(formatter.create_list(info, args))
    print(formatter.create_list_end())

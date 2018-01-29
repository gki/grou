# -*- coding: utf-8 -*-
"""Converter for raw string log to Merge Info."""

import logging
import re
from git_info_converter import GithubInfoConverter
from common import Purpose, MergeInfo


def convert_to_info(base_url, line, options):
    """Convert 1 line log to MergeInfo."""
    logging.debug('rawline = ' + str(line))
    # create dictionary for each merge log.
    splitted_log = line.decode('utf-8').split(':')
    # Get PR number
    if len(splitted_log[2]) == 0 or len(splitted_log[3]) == 0 \
            or re.search('#[0-9]*', splitted_log[3]) is None:
        logging.debug('Ignore unexpected merge log: ' + str(line))
        return None, None
    review_num = GithubInfoConverter.pickup_review_num(splitted_log[3])
    url = GithubInfoConverter.convert_to_review_url(base_url, review_num)
    # Detect PR type
    purpose = Purpose.Unknown
    body = splitted_log[2]
    if bool(re.match('Feature/', body, re.I)):
        purpose = Purpose.Feature
    elif bool(re.match('Bug[fix]*/', body, re.I)):
        purpose = Purpose.BugFix
    elif bool(re.match('Chore/', body, re.I)):
        purpose = Purpose.Chore
    elif bool(re.match('HotFix/', body, re.I)):
        purpose = Purpose.HotFix

    # Format body
    if options.use_commit_body is False:
        body = splitted_log[3]
    elif purpose != Purpose.Unknown:
        body = body.split('/', 1)[1]

    # remove text by using option
    if options.remove_regix:
        logging.debug('before = ' + body)
        body = re.sub(options.remove_regix, '', body).strip()
        logging.debug('after  = ' + body)
    if options.remove_regix_i:
        logging.debug('before = ' + body)
        body = re.sub(options.remove_regix_i, '', body, flags=re.I).strip()
        logging.debug('after  = ' + body)

    info = MergeInfo(commit=str(splitted_log[0]),
                     auther=splitted_log[1],
                     body=body.title(),
                     review_url=url,
                     review_num=review_num,
                     purpose=purpose)
    logging.debug(info)
    return (purpose, info)

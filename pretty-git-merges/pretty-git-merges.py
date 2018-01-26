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
from common import Purpose, ReviewNumPlace, Mode, MergeInfo

args = argument_helper.setup_args()

# Log level setting from command line args
loglevel = logging.ERROR
if args.debug:
    loglevel = logging.DEBUG
logging.basicConfig(format='%(asctime)s %(levelname)s'
                           ' %(message)s', level=loglevel)
logging.debug(args)

# get organization and repo name from git config.
cmd = 'git config remote.origin.url'.split(' ')
remote_url = subprocess.check_output(cmd)
if len(remote_url) == 0:
    logging.error('No remote.origin.url setting for git. Please set origin.\n'
                  'e.g.) '
                  'git remote add origin git@github.com:yourorg/yourrepo.git')
    sys.exit(1)

# TODO Currently confimed only Github. Should check other service like GitLab.
REPO_WEB_URL = remote_url.decode('utf-8') \
                         .replace('\n', '') \
                         .replace(':', '/') \
                         .replace('git@', 'https://') \
                         .replace('.git', '')

# use inputted branch name
cmd = 'git log --first-parent ' + args.branch \
      + ' --merges --pretty=format:%h:%an:%b:%s'
cmd = cmd.split(' ')

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
    review_num_texts = []
    if style == Mode.md.name:
        texts.append('-')

        if options.no_hash is False:
            texts.append(' `{0.commit}`'.format(info))
        texts.append(' {0.body}'.format(info))

        if options.no_auther is False:
            texts.append(' by {0.auther}'.format(info))

        # create review number and link
        review_num_texts.append(' [PR{0.review_num}]'.format(info))
        if options.no_link is False:
            review_num_texts.append('({0.review_url})'.format(info))

    elif style == Mode.html.name:
        texts.append('<li>')
        if options.no_hash is False:
            texts.append(' <code>{0.commit}</code>'.format(info))
        texts.append(' {0.body}'.format(info))
        if options.no_auther is False:
            texts.append(' by {0.auther}'.format(info))

        # create review number and link
        if options.no_link is False:
            review_num_texts.append('<a href="{0.review_url}">'.format(info))
        review_num_texts.append('PR{0.review_num}'.format(info))
        if options.no_link is False:
            review_num_texts.append('</a>'.format(info))
        texts.append('</li>')

    # insert or append review number and link
    if options.show_review_num == ReviewNumPlace.head.name:
        texts.insert(1, ''.join(review_num_texts))
    elif options.show_review_num == ReviewNumPlace.tail.name:
        texts.extend(review_num_texts)

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

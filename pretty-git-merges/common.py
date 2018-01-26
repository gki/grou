# -*- coding: utf-8 -*-
"""Common enum and so on."""
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

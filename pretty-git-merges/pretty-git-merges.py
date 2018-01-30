# -*- coding: utf-8 -*-
"""Main script for pretty git merges."""

# TODO Test
# TODO pip release

import git_info_converter
import merge_info_converter
from merge_info_formatter import OutputFomatterFactory
from common import Purpose, setup_commandline_args, setup_logger

args = setup_commandline_args()
setup_logger(args.debug)
base_url = git_info_converter.create_base_url()
lines = git_info_converter.create_git_merge_logs(args.branch, args.f, args.t)

release_dict = {purpose: [] for purpose in Purpose}
for line in lines:
    purpose, info = merge_info_converter.convert_to_info(base_url, line, args)
    if purpose is None or info is None:
        continue
    release_dict[purpose].append(info)

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

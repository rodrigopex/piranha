#!/usr/bin/python3
import argparse
import ast
import os

from collections import namedtuple
from functools import partial
from pathlib import Path

from redbaron import IfelseblockNode, NodeList, RedBaron

FeatureFlagsParams = namedtuple(
    "FeatureFlagsParams",
    "client_name enable_method_name feature_name remove_if")


def find_freature_flag(feature_flags_parameters: FeatureFlagsParams, value):
    try:
        if (value[0].value == feature_flags_parameters.client_name) and (
                value[1].value == feature_flags_parameters.enable_method_name
        ) and (value[2].value[0].value.value ==
               feature_flags_parameters.feature_name):
            return True
    except IndexError:
        pass


def remove_feature(node, remove_if=True):
    parent = node.parent
    while parent:
        if type(parent) == IfelseblockNode:
            print("found ifelse block!")
            ifelseblock = parent
            new_position = ifelseblock.index_on_parent
            new_parent = ifelseblock.parent
            print(" >>> New parent:", new_position, type(new_parent))
            new_parent.help(deep=1)
            array_ref = new_parent
            if type(new_parent) != RedBaron:
                array_ref = new_parent.value
            rescue_node = ifelseblock.value[0]
            if remove_if:
                try:
                    rescue_node = ifelseblock.value[1]
                except IndexError:
                    rescue_node = None
            array_ref.pop(new_position)
            if rescue_node:
                for position, sub_node in enumerate(rescue_node.value,
                                                    new_position):
                    array_ref.insert(position, sub_node)
                    break
            return
        else:
            parent = parent.parent


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-s',
                        '--source',
                        help='Path of input file for refactoring',
                        required=True)

    parser.add_argument('-f',
                        '--flag',
                        help='Name of the stale flag',
                        required=True)

    # parser.add_argument('p',
    #                     '--properties',
    #                     help='Path of configuration file for Piranha',
    #                     required=True)

    # parser.add_argument(
    #     'o',
    #     '--output',
    #     help=
    #     'Destination of the refactored output. File is modified in-place by default.'
    # )

    # parser.add_argument(
    #     't',
    #     '--treated',
    #     help=
    #     'If this option is supplied, the flag is treated, otherwise it is control.',
    #     nargs='+')

    # parser.add_argument(
    #     'n',
    #     '--max_cleanup_steps',
    #     help=
    #     'The number of times literals should be simplified. Runs until fixed point by default.',
    #     type=int)

    # parser.add_argument('c',
    #                     '--keep_comments',
    #                     help='To keep all comments',
    #                     action_store=True)

    args = parser.parse_args()

    for folder, dirs, files in os.walk(args.source):
        for file in files:
            input_file = Path("{}/{}".format(folder, file))
            with input_file.open("r") as code_stream:
                print("=== BEFORE ===================================")
                code = code_stream.read()
                print(code)
                red = RedBaron(code)
                # red.help(True)
                current = FeatureFlagsParams("client", "is_enabled", f'"{args.flag}"',
                                            False)
                for node in red.find_all("AtomtrailersNode",
                                        value=partial(find_freature_flag, current)):
                    remove_feature(node, remove_if=current.remove_if)
                print("\n\n=== AFTER ====================================")
                print(red)

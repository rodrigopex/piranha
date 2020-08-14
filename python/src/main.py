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
        ) and (not isinstance(value[2].value[0], str) and not isinstance(value[2].value[0].value, str) 
            and value[2].value[0].value.value == feature_flags_parameters.feature_name):
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
                        default='../../great-domestic-ui')

    parser.add_argument('-f',
                        '--flag',
                        default='INTERNATIONAL_CONTACT_TRIAGE_ON',
                        help='Name of the stale flag')

    parser.add_argument('-m',
                        '--model',
                        default='settings',
                        help='flag model')

    parser.add_argument('-mt',
                        '--method',
                        default='FEATURE_FLAGS',
                        help='flag method')


    args = parser.parse_args()

    for folder, dirs, files in os.walk(args.source):
        for file in files:
            if ".py" in file:
                input_file = Path("{}/{}".format(folder, file))
                with input_file.open("r") as code_stream:
                    try:
                        code = code_stream.read()   
                        red = RedBaron(code)

                        print("=== BEFORE ===================================")
                        print(code)
                        
                        # red.help(True)
                        # current = FeatureFlagsParams("client", "is_enabled", f'"{args.flag}"',
                        #                             False)
                        current = FeatureFlagsParams(args.model, args.method, f'"{args.flag}"',
                                                    False)
                        removed = False
                        for node in red.find_all("AtomtrailersNode",
                                                value=partial(find_freature_flag, current)):
                            remove_feature(node, remove_if=current.remove_if)
                            removed = True

                        if removed:    
                            print("\n\n=== AFTER ====================================")
                            print(red)

                            print("accept change? (yes/no)")

                            response = input()

                            if response == "yes":
                                input_file.write_text(red.dumps())
                    except:
                        print()
                        

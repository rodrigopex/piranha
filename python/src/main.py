#!/usr/bin/python3
import argparse
# import ast
import os
import re
from collections import namedtuple
from functools import partial
from pathlib import Path

import colored
from colored import stylize
from redbaron import AssignmentNode, IfelseblockNode, NodeList, RedBaron

FeatureFlagsParams = namedtuple(
    "FeatureFlagsParams",
    "client_name enable_method_name feature_name remove_if")


def find_feature_flag_in_jinja(code, feature_flag, model):
    regex = "{%\s*if\s*" + model + "." + feature_flag + "\s*(.*?)\s\s*%}"
    feature_flag_headers = re.findall(regex, code)
    if len(feature_flag_headers) > 0:
        find_sentence = "{% if " + model + "." + feature_flag + " "
        start_index = code.find(find_sentence + feature_flag_headers[0])
        end_index = code[start_index:len(code)].find("endif %}") + start_index
        return code[start_index:end_index]


def remove_feature_flag_in_jinja(full_code, code_snippet):
    return full_code.replace(code_snippet, "")


def find_django_flags_dict(feature_flags_parameters: FeatureFlagsParams,
                           value):
    try:
        if str(value.parent.target) == "FLAGS":
            return True
    except IndexError:
        pass
    except Exception as err:
        print("Unexpected error:", err)


def find_django_flags(feature_flags_parameters: FeatureFlagsParams, value):
    try:
        if (value[0].value == feature_flags_parameters.enable_method_name
            ) and (str(value[1].value[0].value) ==
                   feature_flags_parameters.feature_name):
            return True
    except IndexError:
        pass


def find_freature_flag(feature_flags_parameters: FeatureFlagsParams, value):
    try:
        if (value[0].value == feature_flags_parameters.client_name) and (
                value[1].value == feature_flags_parameters.enable_method_name
        ) and (not isinstance(value[2].value[0], str)
               and not isinstance(value[2].value[0].value, str) and value[2].
               value[0].value.value == feature_flags_parameters.feature_name):
            return True
    except IndexError:
        pass


def remove_feature_flag_from_settings(
    feature_flags_parameters: FeatureFlagsParams, node):
    for index, child in enumerate(node.value.value):
        key = str(child.key).replace("'", "").replace('"', "")
        if key == feature_flags_parameters.feature_name.replace("'",
                                                                "").replace(
                                                                    '"', ""):
            node.value.value.pop(index)
            break


def remove_feature(node, remove_if=True):
    parent = node.parent
    while parent:
        if type(parent) == IfelseblockNode:
            ifelseblock = parent
            new_position = ifelseblock.index_on_parent
            new_parent = ifelseblock.parent
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
                        default='PROTOTYPE_PAGES_ON',
                        help='Name of the stale flag')

    parser.add_argument('-m', '--model', default='features', help='flag model')

    parser.add_argument('-mt',
                        '--method',
                        default='FEATURE_FLAGS',
                        help='flag method')

    args = parser.parse_args()

    print("#" * 65)
    print("# PIRANHA for Django-flags".ljust(64) + "#")
    print("#" * 65)

    print(f"""
 *** Trying to remove flag:
     * Format: {args.method}('{args.flag}')
     * Folder: {args.source}
    """)
    for folder, dirs, files in os.walk(args.source):
        for file in files:
            if ".py" in file:
                print(f"File: {folder}/{file}   ", end='')
                input_file = Path("{}/{}".format(folder, file))
                with input_file.open("r") as code_stream:
                    try:
                        code = code_stream.read()
                        current = FeatureFlagsParams(args.model, args.method,
                                                     f"'{args.flag}'", True)
                        removed = False
                        settings_file = False
                        if current.feature_name not in code:
                            if "FLAGS = {" in code:
                                print(
                                    f"{colored.fg('black')}{colored.bg('light_blue')} SETTINGS FILE FOUND {colored.attr('reset')}"
                                )
                                settings_file = True
                            else:
                                print(
                                    f"{colored.fg('black')}{colored.bg('orange_3')} FLAG NOT FOUND {colored.attr('reset')}"
                                )
                                continue
                        else:
                            print(
                                f"{colored.fg('black')}{colored.bg('green')} FLAG FOUND {colored.attr('reset')}"
                            )
                        red = RedBaron(code)
                        if settings_file:
                            a = red.find_all("AssignmentNode",
                                             value=partial(
                                                 find_django_flags_dict,
                                                 current))
                            for node in a:
                                remove_feature_flag_from_settings(
                                    current, node)
                                removed = True
                        else:
                            for node in red.find_all("AtomtrailersNode",
                                                     value=partial(
                                                         find_django_flags,
                                                         current)):
                                remove_feature(node,
                                               remove_if=current.remove_if)
                                removed = True

                        if removed:
                            print(
                                "=== BEFORE ==================================="
                            )
                            print(code)
                            print(
                                "\n\n=== AFTER ===================================="
                            )
                            print(red.dumps())

                            print("accept change? (y/[n])")

                            response = input()

                            if response.lower() == "y":
                                print("[y] chosen: file changed!\n")
                                input_file.write_text(red.dumps())
                            else:
                                print("[n] chosen: file not changed!\n")
                    except KeyboardInterrupt:
                        exit(0)
                    except:
                        print("\n\n\nERROR\n\n\n")
            elif ".html" in file:
                input_file = Path("{}/{}".format(folder, file))
                with input_file.open("r") as code_stream:
                    try:
                        code = code_stream.read()
                        code_snippet = find_feature_flag_in_jinja(
                            code, args.flag, args.model)

                        if code_snippet:
                            print(
                                "=== BEFORE ==================================="
                            )
                            print(code)
                            print(
                                "\n\n=== AFTER ===================================="
                            )

                            code_after = remove_feature_flag_in_jinja(
                                code, code_snippet)
                            print(code_after)

                            print("accept change? (yes/no)")

                            response = input()

                            if response == "yes":
                                input_file.write_text(code_after)
                    except:
                        print()

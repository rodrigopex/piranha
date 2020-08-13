#!/usr/bin/python3
import argparse
import ast
from collections import namedtuple
from functools import partial
from pathlib import Path

from redbaron import RedBaron

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


def find_if_parent(node):
    #@TODO: deveria procurar o pai em caso de uma expressão dentro do if.
    #Se o if não for o pai imediato da chamada do método que  habilita a feature, dá pau.
    pass


def remove_feature(node, remove_if=True):
    node_grandpa = node.parent.parent
    new_position = node_grandpa.index_on_parent
    new_parent = node_grandpa.parent
    rescue_node = node_grandpa.value[0]
    if remove_if:
        try:
            rescue_node = node_grandpa.value[1]
        except IndexError:
            rescue_node = None
    new_parent.pop(new_position)
    if rescue_node:
        for position, sub_node in enumerate(rescue_node.value, new_position):
            new_parent.insert(position, sub_node)

    # print(node_grandpa.help())
    # print(rescue_node)
    # print(new_parent)
    # print(new_parent)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('s',
                        '--source',
                        help='Path of input file for refactoring',
                        required=True)

    parser.add_argument('f',
                        '--flag',
                        help='Name of the stale flag',
                        required=True)

    parser.add_argument('p',
                        '--properties',
                        help='Path of configuration file for Piranha',
                        required=True)

    parser.add_argument(
        'o',
        '--output',
        help=
        'Destination of the refactored output. File is modified in-place by default.'
    )

    parser.add_argument(
        't',
        '--treated',
        help=
        'If this option is supplied, the flag is treated, otherwise it is control.',
        nargs='+')

    parser.add_argument(
        'n',
        '--max_cleanup_steps',
        help=
        'The number of times literals should be simplified. Runs until fixed point by default.',
        type=int)

    parser.add_argument('c',
                        '--keep_comments',
                        help='To keep all comments',
                        action_store=True)

    args = parser.parse_args()

    input_file = Path("./samples/ex01.py")
    with input_file.open("r") as code_stream:
        print("=== BEFORE ===================================")
        code = code_stream.read()
        print(code)
        red = RedBaron(code)
        current = FeatureFlagsParams("client", "is_enabled", '"feature 1"',
                                     True)
        for node in red.find_all("AtomtrailersNode",
                                 value=partial(find_freature_flag, current)):
            remove_feature(node, remove_if=current.remove_if)
        print("\n\n=== AFTER ====================================")
        print(red)

#!/usr/bin/python3
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

from typing import Optional

import yaml
import argparse
import pathlib
from os.path import exists
from types import FunctionType


def set_existing_defaults(argparser: argparse.ArgumentParser, **kwargs):
    """
    Works the same as argparser.set_default except it does not create new arguments.
    :param argparser:
    :param kwargs:
    :return:
    """
    for kwarg in kwargs:
        if kwarg in argparser._defaults:
            argparser._defaults.update(kwarg)
    for action in argparser._actions:
        if action.dest in kwargs:
            action.default = kwargs[action.dest]
    return argparser

def combine_namespaces(main_namespace, **aux_namespaces):
    """
    Adds a dictionary of auxiliary namespaces to a main namespace
    :param main_namespace:
    :param aux_namespaces:
    :return:
    """
    for key,val in aux_namespaces.items():
        setattr(main_namespace, key, val)
    return main_namespace

def create_custom_argparser(name: str, arguments_fnc: FunctionType, default_value: Optional[dict] = None):
    """
    Creates an argparser and adds all the arguments in argument_fnc to it, and sets the default values according to default_value.
    """
    named_parser = argparse.ArgumentParser(name)
    named_parser = arguments_fnc(named_parser)
    if default_value:
        named_parser = set_existing_defaults(named_parser, **default_value)
    sub_args = named_parser.parse_args()
    return sub_args

def create_custom_argparsers(names: list[str], argument_fncs: list[FunctionType], default_values: Optional[dict] = None):
    """
    Creates a dictionary of namespaces.
    :param names: a list of the names for the various namespaces
    :param argument_fncs: a list of add_arguments for the corresponding namespace
    :param default_values: a nested dictionary of default values for the argparser.
    :return:
    """
    aux_args = {}
    for name, argument_fnc in zip(names,argument_fncs):
        if default_values:
            aux_args[name] = create_custom_argparser(name, argument_fnc, default_values[name])
        else:
            aux_args[name] = create_custom_argparser(name, argument_fnc)
    return aux_args


def data_args(parser: argparse.ArgumentParser):
    parser.add_argument('--path_train',type=pathlib.Path, help='Path to the training samples')
    parser.add_argument('--path_val',type=pathlib.Path, help='Path to the validation samples')
    parser.add_argument('--path_test',type=pathlib.Path, help='Path to the test samples')
    return parser

def network_args(parser: argparse.ArgumentParser):
    parser.add_argument('--network_type',type=str, choices=['lstm', 'mlp'], help='Choose the network architecture type')
    parser.add_argument('--lr',type=float, default=0.5, help='Learning rate')
    return parser

def main_args(parser: argparse.ArgumentParser):
    parser.add_argument('--path_out',type=pathlib.Path, default='./results/', help='The base folder where all output is saved')
    return parser

def prelim_args(parser: argparse.ArgumentParser):
    parser.add_argument('--config_file',type=pathlib.Path, default='config.yaml', help='If this is given it should set default for the other argparser arguments')
    return parser




def parse_args():
    groups = ['data', 'network']
    arg_fncs = [data_args, network_args]

    # First we create the full parser in a flat structure, this is needed for the argparser to behave well when probed on the command line
    parser_flat = argparse.ArgumentParser("My awesome program")
    parser_flat = main_args(parser_flat)
    parser_flat = prelim_args(parser_flat)
    for group, arg_fnc in zip(groups,arg_fncs):
        parser_flat = arg_fnc(parser_flat)
    _ = parser_flat.parse_args()

    # Next we create the preliminary argparser
    parser_prelim = argparse.ArgumentParser("Prelim")
    parser_prelim = prelim_args(parser_prelim)
    args_prelim = parser_prelim.parse_args()
    if exists(args_prelim.config_file):
        try:
            with open(args_prelim.config_file, 'r') as f:
                conf = yaml.safe_load(f)
        except IOError:
            print(f"Failed to load {args_prelim.config_file} as a yaml file.")
    else:
        conf = None

    # Next we create the main argparser
    parser_main =  argparse.ArgumentParser("Main")
    parser_main = main_args(parser_main)
    parser_main = set_existing_defaults(parser_main,**conf) # Note that we use set_existing_defaults before loading in the preliminary.
    parser_main = prelim_args(parser_main)
    args_main = parser_main.parse_args()

    aux_args = create_custom_argparsers(groups, arg_fncs, conf)
    args = combine_namespaces(args_main, **aux_args)
    return args






if __name__ == '__main__':
    args = parse_args()
    print(args)


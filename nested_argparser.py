import argparse
import pathlib
from copy import deepcopy
from os.path import exists
from types import FunctionType
from typing import Optional

import yaml

def parse_nested_argparser(argparser_groups: dict, description: str = "My awesome program"):
    """
    First it creates the full parser in a flat structure, this is needed for the argparser to behave well when probed on the command line
    Secondly it loads in the preliminary arguments.
    Finally, it creates all the different argparsers and returns a dictionary of parsers.

    Argparser_groups have two reserved keywords: main and preliminary.
        main and preliminary gets combined to a flat group of arguments, while all other keyword groups are created as nested Namespaces.
        preliminary is preloaded before anything else such that those arguments can use to set default values to other arguments, in particular it is currently used to load configurations from a yaml file


    :param argparser_groups:
    :return:
    """
    # First we create the full parser in a flat structure, this is needed for the argparser to behave well when probed on the command line
    parser_flat = argparse.ArgumentParser(description)
    for key, val in argparser_groups.items():
        parser_flat = val(parser_flat)
    _ = parser_flat.parse_args()

    # Next we create the preliminary argparser, which ensures we get the default values from the conf file. This is also where any other preliminary values that we for some reason need to load before gets loaded.
    conf = None
    if "preliminary" in argparser_groups:
        parser_prelim = argparse.ArgumentParser("Prelim")
        parser_prelim = argparser_groups['preliminary'](parser_prelim)
        args_prelim = parser_prelim.parse_args()
        if exists(args_prelim.config_file):
            try:
                with open(args_prelim.config_file, 'r') as f:
                    conf = yaml.safe_load(f)
            except IOError:
                print(f"Failed to load {args_prelim.config_file} as a yaml file.")

    # Finally we create the main argparser
    parser_main =  argparse.ArgumentParser("Main")
    sub_args = argparser_groups.pop("main", None)
    if sub_args is not None:
        parser_main = sub_args(parser_main)
        try:
            parser_main = set_existing_defaults(parser_main,**conf) # Note that we use set_existing_defaults before loading in the preliminary.
        except:
            pass
    sub_args = argparser_groups.pop("preliminary", None)
    if sub_args is not None:
        parser_main = sub_args(parser_main)
    args_main = parser_main.parse_args()
    aux_args = create_custom_argparsers(argparser_groups, conf)
    args = combine_namespaces(args_main, **aux_args)
    return args

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

def create_custom_argparsers(sub_args: dict, default_values: Optional[dict] = None):
    """
    Creates a dictionary of namespaces.
    :param default_values: a nested dictionary of default values for the argparser.
    :return:
    """
    aux_args = {}
    for name, argument_fnc in sub_args.items():
        try: # By using try we can also handle incomplete configuration files that only have some group values.
            aux_args[name] = create_custom_argparser(name, argument_fnc, default_values[name])
        except:
            aux_args[name] = create_custom_argparser(name, argument_fnc)
    return aux_args

def save_configuration_file(filename: pathlib.Path, args, write_all_parameters= False):
    """
    This will save a nested namespace as a configuration yaml file.

    It converts the namespaces to dictionary objects and convert all posix paths into strings.
    :param filename:
    :param args:
    :param write_all_parameters: Does not write variables that are None or empty
    :return:
    """
    def fix_dict(dict_obj):
        for key, val in list(dict_obj.items()): # List makes a copy, such that we can delete while iterating
            if not write_all_parameters and (val is None or val is ''):
                del dict_obj[key]
            elif isinstance(val, pathlib.Path):
                dict_obj[key] = str(val)
            elif isinstance(val, argparse.Namespace):
                dict_obj_sub = val.__dict__
                dict_obj_sub = fix_dict(dict_obj_sub)
                dict_obj[key] = dict_obj_sub
        return dict_obj

    cfg = deepcopy(args)
    # First we convert all posix paths to strings
    cfg_dict = cfg.__dict__
    cfg_dict = fix_dict(cfg_dict)

    with open(filename, 'w') as f:
        yaml.dump(cfg_dict, f)
    return

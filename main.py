import json
from copy import deepcopy
from typing import Optional

import yaml
import argparse
import pathlib
from os.path import exists
from types import FunctionType

from args import data_args, prelim_args, network_args, main_args
from nested_argparser import parse_nested_argparser, save_configuration_file


def parse_args():

    dict_args = {
        'main': main_args,
        'preliminary': prelim_args,
        'data': data_args,
        'network': network_args,
    }
    args = parse_nested_argparser(dict_args)
    filename = 'test.yaml'
    save_configuration_file(filename, args)

    return args






if __name__ == '__main__':
    args = parse_args()
    print(args)


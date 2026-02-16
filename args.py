import argparse
import pathlib

def main_args(parser: argparse.ArgumentParser):
    parser.add_argument('--path_out',type=pathlib.Path, default='./results/', help='The base folder where all output is saved')
    return parser

def prelim_args(parser: argparse.ArgumentParser):
    parser.add_argument('--config_file',type=pathlib.Path, default='config.yaml', help='Set default value for the other argparser arguments. CLI values will still overwrite this')
    return parser

def data_args(parser: argparse.ArgumentParser):
    parser.add_argument('--path_train',type=pathlib.Path, help='Path to the training samples')
    parser.add_argument('--path_val',type=pathlib.Path, help='Path to the validation samples')
    parser.add_argument('--path_test',type=pathlib.Path, help='Path to the test samples')
    return parser

def network_args(parser: argparse.ArgumentParser):
    parser.add_argument('--network_type',type=str, choices=['lstm', 'mlp'], help='Choose the network architecture type')
    parser.add_argument('--lr',type=float, default=0.5, help='Learning rate')
    return parser



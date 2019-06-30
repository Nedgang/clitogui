"Clitogui can handle subparsers !"

import os
import argparse
import clitogui


@clitogui.on
def cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='CLI for messing with clitogui.')
    subparsers = parser.add_subparsers()
    sub1 = subparsers.add_parser('sub1')
    sub1.add_argument('sub1_arg', type=str)
    sub2 = subparsers.add_parser('sub2')
    sub2.add_argument('sub2_arg', type=str)
    return parser


if __name__ == "__main__":
    args = cli_parser().parse_args()

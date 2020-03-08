import argparse
from clitogui import clitogui


@clitogui.clitogui
def cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", type=str)
    parser.add_argument("dpi", type=int, default=300)
    parser.add_argument("factor", type=float, default=0.1)
    return parser


print(cli().parse_args())

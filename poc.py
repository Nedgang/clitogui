#!/usr/bin/python3
"""
Documentation à la fois magnifique et concise.
"""

##########
# IMPORT #
##########
import argparse

from clitogui.clitogui import clitogui

########
# MAIN #
########
def main(parser):
    """
    Bêta test crash main.
    """
    args = parser.parse_args()

    # try:
    answer = args.square**2
    if args.verbose:
        print("The square of {} equals {}".format(args.square, answer))
    else:
        print(answer)
    # except:
        # print("Fin du test")

#############
# FUNCTIONS #
#############
@clitogui
def create_parser() -> argparse.ArgumentParser:
    """
    Function to define the parser
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('square', help="Display a square of a given number",\
                        type=int)
    parser.add_argument('-v', '--verbose', help="Increase output verbosity",\
                        action="store_true")
    parser.add_argument('-i','--iteration', type=int, choices=[0, 1, 2],\
                        help="Iterations number")
    parser.add_argument('--sum', dest='accumulate', action='store_const',
                    const=sum, default=max,
                    help='sum the integers (default: find the max)')
    # parser.add_argument('--foo', help="Test append action", action='append')
    return parser

##########
# LAUNCH #
##########
if __name__ == "__main__":
    main(create_parser())

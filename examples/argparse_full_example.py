"A fully featured example of argparse parser that clitogui can encapsulate"

import os
import argparse
import clitogui

LOGLEVELS = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')

@clitogui.on
def cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='CLI for messing with clitogui.')
    parser.add_argument('infile', type=existant_file, default=__file__,
                        help='file containing the graph data')
    parser.add_argument('--outfile', '-o', type=writable_file,
                        help='output file. Will be overwritted')
    parser.add_argument('--loglevel', choices=LOGLEVELS,
                        help='Logging level, one of ' + ', '.join(LOGLEVELS) + '.')
    parser.add_argument('--seed', type=int, default=0,
                        help='A random seed ; if 0 or not given, a random one will be chosen')
    parser.add_argument('--logfile', type=writable_file, help='Logging file')
    parser.add_argument('--all-signal', action='store_true',
                        help='Send all possible signals')
    parser.add_argument('--thread', type=thread_number, default=1,
                        help='Number of thread to use during solving')
    return parser


def thread_number(nbt:int) -> int:
    """Argparse type, raising an error if given thread number is non valid"""
    nbt = int(nbt)
    if not isinstance(nbt, int):
        raise argparse.ArgumentTypeError(
            "Given number of thread ({}) is an {} not an integer.".format(nbt, type(nbt))
        )
    if int(nbt) < 1:
        raise argparse.ArgumentTypeError(
            "Given number of thread ({}) is not valid.".format(nbt)
        )
    return nbt


def existant_file(filepath:str) -> str:
    """Argparse type, raising an error if given file does not exists"""
    if not os.path.exists(filepath):
        raise argparse.ArgumentTypeError("file {} doesn't exists".format(filepath))
    return filepath


def writable_file(filepath:str) -> str:
    """Argparse type, raising an error if given file is not writable.
    Will delete the file !

    """
    try:
        with open(filepath, 'w') as fd:
            pass
        os.remove(filepath)
        return filepath
    except (PermissionError, IOError):
        raise argparse.ArgumentTypeError("file {} is not writable.".format(filepath))


def elem_in_list(elements:iter):
    def valid_element(element:str) -> str:
        """Argparse type, raising an error if given value is not expected"""
        if element not in elements:
            raise argparse.ArgumentTypeError(f"Value {element} is unexpected. Valid inputs: " + ', '.join(map(str, elements)))
        return element
    return valid_element


if __name__ == "__main__":
    print('NOGUI:', cli_parser().parse_args([__file__]))  # shouldn't run a GUI
    print('WITH GUI:', cli_parser().parse_args())  # should run a GUI

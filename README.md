# CLItoGUI
Python extension to generate a GUI from argparse CLI.

## Version:
alpha

## Used packages:
- pyQt5

## Supported parser:
 - Argparse

## TODO List before bêta:
- Testing
- Reformating
- Bug hunt
- Documentation

## Usage:
Just add the decorator to the main or parser function:

    from clitogui import clitogui

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
        return parser

## How does it work?:
TODO

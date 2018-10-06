# CLItoGUI
Python package to generate a GUI from argparse CLI.

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

## Used packages:
- pyQt5

## Supported parser:
 - Argparse

## Supported GUI:
- PyQt

## TODO List before bêta:
- Support for Tkinter (add `Environment :: X11 Applications :: GTK`)
- Define Model
- Add one simple test of parsing to Model

## How does it work?:
TODO

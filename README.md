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

### Argparse
See [examples/argparse_full_example.py](examples/argparse_full_example.py) for an example of supported features of argparse.

Note that Argparse [custom types](https://docs.python.org/3/library/argparse.html#type) are supported, using type annotations:

    import clitogui

    @clitogui.clitogui
    def create_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser()
        parser.add_argument('infile', type=existant_file)
        return parser

    def existant_file(filepath:str):  # note the type annotation here
        if not os.path.exists(filepath):
            raise argparse.ArgumentTypeError("file {} doesn't exists".format(filepath))
        return filepath

The type annotation will be used to decide the GUI elements to show.

## Supported GUI:
- PyQt

## TODO List before bêta:
- Add one simple test of cli parsing to Model
- Define Model in its own module
- Use of Model for [argument_extractor](clitogui/argument_extractor.py)
- Support for Tkinter (add `Environment :: X11 Applications :: GTK`)
- Support for docopt

## How does it work?:
TODO

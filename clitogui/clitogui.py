#!/usr/bin/python3
"""
Function to alter CLI parsing command.
The new parsing command allow to automaticly generate au GUI and return
argument in a CLI form.
"""

from functools import wraps
from argparse import ArgumentParser

from .argument_extractor import ExtractedParser
from .gui import Interface


def clitogui(parser_function):
    """Decorator for a function returning a parser (such as argparse.ArgumentParser).

    Will patch the returned parser to make it use a GUI when no arguments
    are explicitely provided.

    Cf gui.py for GUI definition.
    """

    def patch_parser(parser):
        "Patch the parser by decorating its parse_args method"
        @wraps(parser.parse_args)
        def parse_args_from_gui(*args, **kwargs):
            """Generate the GUI, and send the returned CLI to the parser"""
            if args or kwargs:
                return parser.old_parse_args(*args, **kwargs)
            # Use of Interface object from gui.py
            gui = Interface(ExtractedParser(parser))
            return parser.old_parse_args(gui.out_args)
        parser.old_parse_args = parser.parse_args
        parser.parse_args = parse_args_from_gui
        return parser

    @wraps(parser_function)
    def decorated_function(*args, **kwargs):
        parser = parser_function(*args, **kwargs)
        if isinstance(parser, ArgumentParser):
            # Saving the old argument parser for later, replacing it by our own
            patch_parser(parser)
        else:
            raise TypeError("Not supported parser: " + repr(parser_func))
        return parser

    return decorated_function

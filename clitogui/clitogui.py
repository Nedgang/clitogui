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
from .interactive_gui import InteractiveInterface


def make_clitogui(gui_object, *args, **kwargs):
    """Build the decorator with given GUI object and its arguments"""

    def clitogui(parser_function):
        """Decorator for a function returning a parser (such as argparse.ArgumentParser).

        Will patch the returned parser to make it use a GUI when no arguments
        are explicitely provided.

        Cf gui.py for GUI definition.
        """

        def patch_parser(parser):
            "Patch the parser by decorating its parse_args method"

            @wraps(parser.parse_args)
            def parse_args_from_gui(*parser_args, **parser_kwargs):
                """Generate the GUI, and send the returned CLI to the parser"""
                if parser_args or parser_kwargs:
                    return parser.old_parse_args(*parser_args, **parser_kwargs)
                # Use of Interface object from gui.py
                gui = gui_object.build_and_run(ExtractedParser(parser), *args, **kwargs)
                return gui.parsed_args()
                # return ret

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

    return clitogui


@wraps(InteractiveInterface)
def make_interactive(*args, **kwargs):
    return make_clitogui(InteractiveInterface, *args, **kwargs)


clitogui = on = make_clitogui(Interface)
interactive = interactively_on = make_interactive

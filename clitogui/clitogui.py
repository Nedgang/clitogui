#!/usr/bin/python3
"""
Function to alter CLI parsing command.
The new parsing command allow to automaticly generate au GUI and return
argument in a CLI form.
"""

##########
# IMPORT #
##########
import sys

from argparse import ArgumentParser

from .argument_extractor import ExtractedParser
from .gui import Interface

#############
# DECORATOR #
#############
def clitogui(parser_function):
    """
    Function to use as a decorator, will be called before the decorated
    function execution.
    Extract arguments from the parser and send them to the GUI constructor
    (cf gui.py).
    """

    def gui_builder(self):
        """
        Generate the GUI, and send the returned CLI to the parser.
        """
        # Use of Interface object from gui.py
        gui = Interface(ExtractedParser(self))
        return self.old_parse_args(gui.out_args)

    # ARGPARSE TO GUI
    def argparse_to_gui(payload):
        """
        Setup GUI build from an argparse parser.
        """

        def argparse_alterator(*args, **kwargs):
            """
            Change ArgParse.parse_args function to the gui_builder function.
            """
            # Saving the old argument parser for later
            ArgumentParser.old_parse_args = ArgumentParser.parse_args
            # Replace the parse_args function by our own, to allow call from
            # the user script
            ArgumentParser.parse_args = gui_builder
            return payload(*args, **kwargs)

        argparse_alterator.__name__ = payload.__name__
        return argparse_alterator

    # Allow to ignore clitogui in the CLI, for testing purpose
    if "--cli" in sys.argv:
        sys.argv.remove("--cli")
        return parser_function
    else:
        if 'argparse' in sys.modules.keys():
            return argparse_to_gui(parser_function)
        else:
            raise TypeError("Not supported parser")

#!/usr/bin/python3
"""
Decorator file.
Everything start from here.
"""

##########
# IMPORT #
##########
import argparse
import sys

from argparse import ArgumentParser
from collections import defaultdict

from .argument_extractor import Extracted_parser
from .gui import Interface

#############
# DECORATOR #
#############
def clitogui(parser_function):
    """
    To add on the parser function.
    Extract arguments from the parser and send them to the GUI constructor
    (cf gui.py).
    """

    # ARGPARSE TO GUI
    def argparse_to_gui(payload):
        """
        Function to setup the build of the GUI, from an argparse parser.
        """

        def gui_builder(self):
            """
            Generate the GUI, save arguments back from it, and build the CLI
            for the parser.
            """
            # Use of Interface object from gui.py
            gui = Interface(Extracted_parser(self))
            return self.old_parse_args(gui.out_args)

        def argparse_alterator(*args, **kwargs):
            """
            Change ArgParse.parse_args function.
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
        return argparse_to_gui(parser_function)

#!/usr/bin/python3
"""

"""

##########
# IMPORT #
##########
import argparse
import sys
import tkinter as tk

from argparse import ArgumentParser
from collections import defaultdict

from .gui import Interface

IGNORE_COMMAND = "--cli"
UNWANTED_ACTION = ["_HelpAction"]

#############
# DECORATOR #
#############
def clitogui(parser_function):
    """
    Decorator with everything in it.
    #gazFactory
    """

    # ARGPARSE TO GUI
    def argparse_to_gui(payload):
        """
        Function to setup the build of the GUI, from an argparse parser.
        """

        def argparse_args_extractor(parser):
            """
            Generation of widgets based on the parser.
            """
            for action in tuple(parser._actions):
                if type(action) != argparse._HelpAction and\
                type(action) != argparse._VersionAction:
                    yield action

        def argparse_gui_builder(self):
            """
            Function to generate the GUI, and return arguments from it.
            """
            root = tk.Tk()
            gui = Interface(root, argparse_args_extractor(self))
            root.mainloop()
            return self.old_parse_args(gui.out_args)

        def argparse_alterator(*args, **kwargs):
            """
            Change ArgParse.parse_args function.
            """
            ArgumentParser.old_parse_args = ArgumentParser.parse_args
            # Here is the deal
            ArgumentParser.parse_args = argparse_gui_builder
            return payload(*args, **kwargs)

        argparse_alterator.__name__ = payload.__name__
        return argparse_alterator

    # Allow to ignore clitogui in CLI
    if IGNORE_COMMAND in sys.argv:
        sys.argv.remove(IGNORE_COMMAND)
        return parser_function
    else:
        return argparse_to_gui(parser_function)

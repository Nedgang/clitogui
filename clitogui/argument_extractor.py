#!/usr/bin/python3
"""
Object used to standardise parser informations.
Supported parser: argparse.
"""

##########
# IMPORT #
##########
import argparse

#########
# CLASS #
#########
class ExtractedParser():
    """
    Contain arguments and subparser list.
    The constructor called depended on the parser used.
    """
    def __init__(self, parser):
        self.arguments = []
        self.subparsers = []
        if isinstance(parser, argparse.ArgumentParser):
            self._argparse_extractor_(parser)
        else:
            raise TypeError("Not supported parser: ", type(parser))

    def _argparse_extractor_(self, parser):
        """
        Constructor used by the ExtractedParser object if the used parser
        is argparse.
        """
        # We don't want help actions
        parser._actions = [x for x in parser._actions \
                           if not isinstance(x, argparse._HelpAction)]
        self.subparsers = [action for action in parser._actions\
                           if isinstance(action, argparse._SubParsersAction)]
        # In case of no subparser:
        if self.subparsers == []:
            for action in parser._actions:
                arg = {}
                arg['cli'] = action.option_strings
                arg['name'] = action.dest
                arg['choices'] = action.choices
                arg['help'] = action.help
                arg['default'] = action.default
                if isinstance(action, argparse._StoreAction):
                    arg['type'] = str
                elif isinstance(action, (argparse._StoreTrueAction, \
                                argparse._StoreConstAction,\
                                argparse._StoreFalseAction)):
                    arg['type'] = bool
                elif isinstance(action, argparse._AppendAction):
                    arg['type'] = "append_action"
                elif isinstance(action, argparse._CountAction):
                    arg['type'] = int
                else:
                    raise TypeError("Unsupported argument type: ", type(action))
                self.arguments.append(arg)

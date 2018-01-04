#!/usr/bin/python3
"""

"""

##########
# IMPORT #
##########
import argparse

#########
# CLASS #
#########
class Extracted_parser():
    """
    """
    def __init__(self, parser):
        self.arguments = []
        if type(parser) == argparse.ArgumentParser:
            self._argparse_extractor_(parser)
        else:
            raise TypeError("Not supported parser: ", type(parser))

    def _argparse_extractor_(self, parser):
        """
        """
        # We don't want help actions
        parser._actions = [x for x in parser._actions \
                           if type(x) != argparse._HelpAction]
        self.subparsers = [action for action in parser._actions\
                           if type(action) == argparse._SubParsersAction]
        # In case of no subparser:
        if self.subparsers == []:
            for action in parser._actions:
                arg = {}
                arg['cli'] = action.option_strings
                arg['name'] = action.dest
                arg['choices'] = action.choices
                arg['help'] = action.help
                arg['default'] = action.default
                if type(action) == argparse._StoreAction:
                    arg['type'] = str
                elif type(action) == argparse._StoreTrueAction or\
                        type(action) == argparse._StoreConstAction or\
                        type(action) == argparse._StoreFalseAction:
                    arg['type'] = bool
                elif type(action) == argparse._AppendAction:
                    arg['type'] = "append_action"
                elif type(action) == argparse._CountAction:
                    arg['type'] = int
                else:
                    raise TypeError("Unsupported argument type: ", type(action))
                self.arguments.append(arg)

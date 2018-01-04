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
        self.subparsers = [action for action in parser._actions\
                           if type(action) == argparse._SubParsersAction]
        if self.subparsers == []:
            for action in parser._actions:
                if type(action) == argparse._HelpAction:
                    pass
                else:
                    arg = {}
                    arg["cli"] = action.option_strings
                    arg["name"] = action.dest
                    arg['choices'] = action.choices
                    arg['help'] = action.help
                    arg['type'] = type(action)
                    self.arguments.append(arg)

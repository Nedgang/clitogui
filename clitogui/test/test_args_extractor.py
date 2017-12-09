import pytest

from clitogui.clitogui import clitogui

import argparse

def test_help_extraction():

    @clitogui
    def create_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser()
        return parser

    parser = create_parser()
    for a in parser._actions: 
        assert type(a) == argparse._HelpAction

def test_version_extraction():

    @clitogui
    def create_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser()
        parser.add_argument('--version', action='version', version='0.1')
        return parser

    parser = create_parser()
    assert any([type(a) == argparse._VersionAction for a in parser._actions])

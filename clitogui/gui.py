#!/usr/bin/python3
"""
File containing the GUI stuff:
- Generation of the window
- Widgets creation
- Arguments return
"""

import sys

import inspect
import argparse

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class Interface(QDialog):
    """Automatized GUI using ExtractedParser object

    To create one instance, use static method `build_and_run`,
    that will start Qt, run the Interface, and return it when closed.

    The properties of interest for client code, once the dialog is closed:
        - out_args: the arguments, as found in sys.argv
        - parsed_args: the arguments, as parsed by the argument parser (such as argparse)

    Note that subclasses can easily override:
        - __init__: to get parameters from the outside
        - _build_interface: to add buttons or other widgets
        - _on_accept: to define a behavior to adopt when the dialog is successfully closed
        - parsed_args: to modify the returned parsed_args object

    See InteractiveInterface for a living subclass example.

    """

    def __init__(self, clitogui_actions):
        """Creation of the window, and associated layout"""
        super().__init__()
        # Arguments final values from widgets
        self.results = {}
        # CLI which will be generated from self.results
        self.out_args = []
        # Interface initialization
        self.parser = clitogui_actions
        self.setLayout(self._build_interface())

    def _build_interface(self):
        "Must return the main layout"
        # Layouts definition
        main_layout = QVBoxLayout()

        # In case of subparser, layout containing widgets is different.
        if self.parser.list_subparsers == []:
            self.has_subparser = False
            self.widget_layout = QFormLayout()
            self.__create_widgets__(self.widget_layout, self.parser.arguments)
            main_layout.addLayout(self.widget_layout)
        else:
            self.has_subparser = True
            self.tabs = QTabWidget()
            self.__create_tabs__()
            main_layout.addWidget(self.tabs)

        # Interaction buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(QCoreApplication.instance().quit)
        main_layout.addWidget(self.buttons)
        return main_layout

    def exec(self):
        # Application initialization
        retval = super().exec()
        if retval == QDialog.Accepted:
            self._on_accept()
        else:
            sys.exit()

    def _on_accept(self):
        "called when exited with 'OK'"
        self.out_args = self.parse_gui()

    @classmethod
    def build_and_run(cls, *args, **kwargs):
        app = QApplication(sys.argv)
        dialog = cls(*args, **kwargs)
        dialog.__app = app  # if forgotten, will throw segfaults
        dialog.exec()
        return dialog

    def parse_gui(self) -> list:
        "Return the list of command-line arguments described by GUI state"
        out_args = []
        if self.has_subparser:
            self.widget_layout = self.tabs.currentWidget().layout
            current_tab_name = self.tabs.tabText(self.tabs.currentIndex())
            # To remplace by a clean method
            current_tab_arguments = [arg for arg in [x['list_actions'] for\
                                    x in self.parser.list_subparsers\
                                   if x['name'] == current_tab_name]][0]
            self.parser.arguments = current_tab_arguments + self.parser.arguments
            out_args.append(current_tab_name)

        self.__widget_recuperation__()

        for arg in self.parser.arguments:
            if arg['type'] is str:
                if arg['cli'] != []:
                    out_args.append(arg['cli'])
                out_args.append(self.results[arg['name']])
            elif arg['type'] is int:
                out_args.append(arg['cli'])
                out_args.append(str(self.results[arg['name']]))
            elif arg['type'] is bool:
                if self.results[arg['name']]:
                    out_args.append(arg['cli'])
            elif arg['type'] == 'append_action':
                for command in self.results[arg['name']].split(' '):
                    out_args.append(arg['cli'])
                    out_args.append(command)
            elif arg['type'] == 'count_action':
                    name, count = arg['cli'], self.results[arg['name']]
                    out_args.extend([name] * count)
            elif callable(arg['type']):
                if arg['cli'] != []:
                    out_args.append(arg['cli'])
                out_args.append(arg['type'](self.results[arg['name']]))  # TODO: intercept argparse exception due to arg['type'] to print them in the GUI
            else:
                raise ValueError("Type {} is unhandled".format(arg['type']))
        # print('OUT ARGS:', out_args)
        return out_args

    def parsed_args(self):
        ret = self.parser.parser.old_parse_args(self.out_args)
        return ret

    def __create_widgets__(self, parent, arguments):
        """
        Function to generate widgets from arguments list in parent layout.
        In: - parent: QLayout
            - arguments: List of arguments formatted by ExtractedParser object.
        Out: a QWidget is added into the parent layout.
        """
        # Creation of arguments widgets
        for action in arguments:
            widget = widget_for_type(action['type'], action['default'], action['choices'])
            widget.setToolTip(action['help'])
            parent.addRow(action['name'], widget)

    def __create_tabs__(self):
        """
        Create in ExtractedParser object the number of tabs needed for
        subparsers.
        """
        for subparser in self.parser.list_subparsers:
            tab = QWidget()
            tab.layout = QFormLayout()
            self.__create_widgets__(tab.layout, subparser["list_actions"])
            self.__create_widgets__(tab.layout, self.parser.arguments)
            tab.setLayout(tab.layout)
            self.tabs.addTab(tab, subparser["name"])

    def __widget_recuperation__(self):
        """
        Allow to file ExtractedParser.results with the values of widgets
        contained into widget_layout.
        """
        for i in range(self.widget_layout.rowCount()):
            # Find the widget at position i
            widget = self.widget_layout.itemAt(i, QFormLayout.FieldRole).widget()
            # Find widget label
            label = self.widget_layout.labelForField(widget).text()
            # Find widget value
            value = widget.metaObject().userProperty().read(widget)
            self.results[label] = value


def widget_for_type(wtype:type, default_value:object, choices:iter=None) -> QWidget:
    """Return initialized widget describing given type with given value"""
    max_int = 2**31 - 1
    if choices is None:
        if wtype is bool:
            widget = QCheckBox()
            try:
                widget.setCheckState(default_value)
            except:
                widget.setCheckState(False)
        elif wtype is str:
            widget = QLineEdit(default_value)
        elif wtype is int:
            widget = QSpinBox()
            widget.setRange(-max_int, max_int)
            widget.setSingleStep(1)
            widget.setValue(int(default_value or 0))
        elif wtype == 'append_action':# or wtype is argparse._AppendAction:
            widget = QLineEdit(default_value)
        elif wtype == 'count_action':
            widget = widget_for_type(int, default_value, choices)
            widget.setRange(0, max_int)
        elif callable(wtype):  # probably an user-defined function
            # expect that the type annotation will provide us some info
            atype = inspect.getfullargspec(wtype).annotations.get('return', None)
            if atype is None:  # no annotation given, we don't know what to do
                raise TypeError("Unhandled type 'custom function {}', because it has no indication of output type".format(wtype.__name__))
            else:
                return widget_for_type(atype, default_value, choices)
        else:
            raise TypeError("Unhandled type: {}".format(wtype))
    else:  # there is a choice to make  (between strings, it sounds necessary)
        widget = QComboBox()
        widget.addItems(tuple(map(str, choices)))
        widget.setCurrentText(str(default_value))
    return widget

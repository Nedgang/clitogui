#!/usr/bin/python3
"""
File containing the GUI stuff:
- Generation of the window
- Widgets creation
- Arguments return
"""

##########
# IMPORT #
##########
import sys

import inspect
import argparse

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

#########
# CLASS #
#########
class Interface():
    """
    Automatized GUI using ExtractedParser object.
    """
    def __init__(self, clitogui_actions):
        """
        Creation of the window, and associated layout.
        """
        # Arguments final values from widgets
        self.results = {}
        # CLI which will be generated from self.results
        self.out_args = []
        # Interface initialization
        self.parser = clitogui_actions
        # GUI configuration
        # Application initialization
        self.application = QApplication(sys.argv)
        # Layouts definition
        self.main_layout = QVBoxLayout()

        # In case of subparser, layout containing widgets is different.
        if self.parser.list_subparsers == []:
            self.has_subparser = False
            self.widget_layout = QFormLayout()
            self.__create_widgets__(self.widget_layout, self.parser.arguments)
            self.main_layout.addLayout(self.widget_layout)
        else:
            self.has_subparser = True
            self.tabs = QTabWidget()
            self.__create_tabs__()
            self.main_layout.addWidget(self.tabs)

        # Interaction buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok\
                                   |QDialogButtonBox.Cancel)
        dialog = QDialog()
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(QCoreApplication.instance().quit)
        self.main_layout.addWidget(buttons)
        dialog.setLayout(self.main_layout)

        # Widgets values recuperation
        if dialog.exec() == QDialog.Accepted:
            if self.has_subparser:
                self.widget_layout = self.tabs.currentWidget().layout
                current_tab_name = self.tabs.tabText(self.tabs.currentIndex())
                # To remplace by a clean method
                current_tab_arguments = [arg for arg in [x['list_actions'] for\
                                        x in self.parser.list_subparsers\
                                       if x['name'] == current_tab_name]][0]
                self.parser.arguments = current_tab_arguments + self.parser.arguments
                self.out_args.append(current_tab_name)

            self.__widget_recuperation__()

            for arg in self.parser.arguments:
                if arg['type'] == str:
                    if arg['cli'] != []:
                        self.out_args.append(arg['cli'])
                    self.out_args.append(self.results[arg['name']])
                elif arg['type'] == int:
                    for i in range(0, self.results[arg['name']]):
                        self.out_args.append(arg['cli'])
                elif arg['type'] == bool:
                    if self.results[arg['name']]:
                        self.out_args.append(arg['cli'])
                elif arg['type'] == 'append_action':
                    for command in self.results[arg['name']].split(' '):
                        self.out_args.append(arg['cli'])
                        self.out_args.append(command)
                elif callable(arg['type']):
                    if arg['cli'] != []:
                        self.out_args.append(arg['cli'])
                    self.out_args.append(arg['type'](self.results[arg['name']]))
                else:
                    raise ValueError("Type {} is unhandled".format(arg['type']))

        else:
            sys.exit()

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
            maxi = 2**31 - 1
            widget.setRange(-maxi, maxi)
            widget.setSingleStep(1)
            widget.setValue(default_value)
        elif wtype == 'append_action':
            widget = QLineEdit(default_value)
        elif wtype is argparse._AppendAction:
            widget = QLineEdit(default_value)
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

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
import os
import sys

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
        # Widgets final values
        self.results = {}
        self.out_args = []
        # Interface data initialization
        self.title = os.path.basename(sys.argv[0]).split(".")[0]
        self.parser = clitogui_actions
        # GUI configuration
        # Application initialization
        self.application = QApplication(sys.argv)
        # Layouts definition
        self.main_layout = QVBoxLayout()

        if self.parser.list_subparsers == []:
            self.widget_layout = QFormLayout()
            self.__create_widgets__(self.widget_layout, self.parser.arguments)
            self.main_layout.addLayout(self.widget_layout)
        else:
            self.tabs = QTabWidget()
            self.__create_tabs__()
            self.main_layout.addWidget(self.tabs)
            self.widget_layout = self.tabs.currentWidget().layout

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
            print(self.tabs.tabText(self.tabs.currentIndex()))
            for i in range(self.widget_layout.rowCount()):
                # Find the widget at position i
                widget = self.widget_layout.itemAt(i, QFormLayout.FieldRole).widget()
                # Find widget label
                label = self.widget_layout.labelForField(widget).text()
                # Find widget value
                value = widget.metaObject().userProperty().read(widget)
                self.results[label] = value

            for arg in self.parser.arguments:
                if arg['cli'] != [] and arg['type'] != 'append_action':
                    self.out_args.append(arg['cli'][0])
                if arg['type'] == str:
                    self.out_args.append(self.results[arg['name']])
                elif arg['type'] == int:
                    for i in range(0, self.results[arg['name']]):
                        self.out_args.append(arg['cli'][0])
                elif arg['type'] == 'append_action':
                    for command in self.results[arg['name']].split(' '):
                        self.out_args.append(arg['cli'][0])
                        self.out_args.append(command)

            print(self.out_args)
        else:
            sys.exit()

    def __create_widgets__(self, parent, arguments):
        # Creation of arguments widgets
        for action in arguments:
            if action['choices'] != None:
                widget = QComboBox()
                widget.addItems([str(i) for i in action['choices']])
            else:
                if action['type'] == bool:
                    widget = QCheckBox()
                    try:
                        widget.setCheckState(action['default'])
                    except:
                        pass
                elif action['type'] == str:
                    widget = QLineEdit(action['default'])
                elif action['type'] == int:
                    widget = QComboBox()
                    widget.addItems([str(i) for i in range[0, 10]])
                elif action['type'] == 'append_action':
                    widget = QLineEdit(action['default'])
                elif action['type'] == argparse._AppendAction:
                    widget = QLineEdit(action['default'])
                else:
                    raise TypeError("Unhandled type: {}".format(action['type']))
            widget.setToolTip(action['help'])
            parent.addRow(action['name'], widget)

    def __create_tabs__(self):
        for subparser in self.parser.list_subparsers:
            tab = QWidget()
            tab.layout = QFormLayout()
            self.__create_widgets__(tab.layout, subparser["list_actions"])
            self.__create_widgets__(tab.layout, self.parser.arguments)
            tab.setLayout(tab.layout)
            self.tabs.addTab(tab, subparser["name"])

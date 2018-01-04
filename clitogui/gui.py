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
    def __init__(self, clitogui_actions, *args, **kwargs):
        # Interface data initialization
        self.title = os.path.basename(sys.argv[0]).split(".")[0]
        self.parser  = clitogui_actions
        self.results  = {} # Widgets final values
        self.out_args = [] # Will be populated with args
        # GUI configuration
        # Application initialization
        self.application = QApplication(sys.argv)

        # LAUNCH WIDGETS CREATION
        self.__create_window__()

    def __create_window__(self):
        """
        Creation of the window, and associated layout.
        """
        # Layouts definition
        widget_layout = QFormLayout()
        main_layout = QVBoxLayout()
        # Interaction buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok\
                                   |QDialogButtonBox.Cancel)
        # Buttons link to dialog box
        dialog = QDialog()
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(QCoreApplication.instance().quit)
        # Layouts relations
        main_layout.addLayout(widget_layout)
        main_layout.addWidget(buttons)
        dialog.setLayout(main_layout)
        # Creation of arguments widgets
        for action in self.parser.arguments:
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
                    widget.addItems([str(i) for i in range[0,10]])
                elif action['type'] == 'append_action':
                    widget = QLineEdit(action['default'])
                elif action['type'] == argparse._AppendAction:
                    widget = QLineEdit(action['default'])
                else:
                    raise TypeError("Unhandled type: {}".format(action['type']))
            widget.setToolTip(action['help'])
            widget_layout.addRow(action['name'], widget)

        # Widgets values recuperation
        if dialog.exec() == QDialog.Accepted:
            for i in range(widget_layout.rowCount()):
                # Find the widget at position i
                widget = widget_layout.itemAt(i, QFormLayout.FieldRole).widget()
                # Find widget label
                label  = widget_layout.labelForField(widget).text()
                # Find widget value
                value  = widget.metaObject().userProperty().read(widget)
                self.results[label] = value

            for arg in self.parser.arguments:
                if arg['cli'] != [] and arg['type'] != 'append_action':
                    self.out_args.append(arg['cli'][0])
                if arg['type'] == str:
                    self.out_args.append(self.results[arg['name']])
                elif arg['type'] == int:
                    for i in range(0,self.results[arg['name']]):
                        self.out_args.append(arg['cli'][0])
                elif arg['type'] == 'append_action':
                    for command in self.results[arg['name']].split(' '):
                        self.out_args.append(arg['cli'][0])
                        self.out_args.append(command)

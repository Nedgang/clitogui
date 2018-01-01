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
        self.actions  = tuple(clitogui_actions)
        self.out_args = [] # Will be populated with args
        self.results  = {} # Widgets final values
        self.hash_table = {}
        print(self.actions)
        for x in self.actions:
            print(type(x))
            if x.option_strings == []:
                self.hash_table[x.dest] = x.option_strings
            else:
                self.hash_table[x.dest] = x.option_strings[0]
        # GUI configuration
        # Application initialization
        self.application = QApplication(sys.argv)

        # LAUNCH WIDGETS CREATION
        self.__create_window__()

    def __create_window__(self):
        """
        Creation of the window, and associated layout.
        """
        # Layouts definition
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
        for action in self.actions:
            if action.choices != None:
                widget = QComboBox()
                widget.addItems([str(i) for i in action.choices])
            else:
                if type(action) == argparse._StoreTrueAction\
                        or type(action) == argparse._StoreFalseAction:
                    widget = QCheckBox()
                    widget.setCheckState(action.default)
                elif type(action) == argparse._StoreConstAction:
                    widget = QCheckBox()
                elif type(action) == argparse._StoreAction:
                    widget = QLineEdit(action.default)
                elif type(action) == argparse._CountAction:
                    widget = QComboBox()
                    widget.addItems([str(i) for i in range[0,10]])
                elif type(action) == argparse._AppendAction:
                    widget = QLineEdit(action.default)
                elif type(action) == argparse._AppendAction:
                    widget = QLineEdit(action.default)
                else:
                    raise TypeError("Unhandled type: {}".format(type(action)))
            widget.setToolTip(action.help)
            widget_layout.addRow(action.dest, widget)
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
            print(self.results)
        # Writing the CLI from widgets values
        print(self.hash_table)
        for dest in self.results:
            if self.hash_table[dest] != []:
                self.out_args.append(self.hash_table[dest])
            self.out_args.append(self.results[dest])
        print(self.out_args)

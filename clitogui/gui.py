#!/usr/bin/python3
"""
File containing the GUI stuff:
- Generation of the window
- Widgets creation
- Arguments return
"""

import io
import sys
import inspect
import argparse
import contextlib


try:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
except ImportError:
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
        - _on_widget_creation: to modify option widgets after their creation

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
        self._version_argument = ""
        self.setLayout(self._build_interface())

    def _build_interface(self):
        "Must return the main layout"
        # In case of subparser, layout containing widgets is different.
        if self.parser.list_subparsers == []:
            self.has_subparser = False
            self.widget_layout = QFormLayout()
            self.__create_widgets__(self.widget_layout, self.parser.arguments)
            wid_options = QWidget()  # make it a widget
            wid_options.setLayout(self.widget_layout)
        else:
            self.has_subparser = True
            self.tabs = QTabWidget()
            self.__create_tabs__()
            wid_options = self.tabs

        # indicate version widget
        wid_version = self.__widget_for_version()

        # Layouts definition
        main_layout = QVBoxLayout()
        if wid_version:
            main_layout.addWidget(wid_version)
        main_layout.addWidget(wid_options)

        # Interaction buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(QCoreApplication.instance().quit)
        main_layout.addWidget(self.buttons)
        return main_layout

    def exec(self):
        # Application initialization
        try:  # Pyside way
            retval = super().exec_()
        except AttributeError:  # PyQt way
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
            current_tab_arguments = [
                arg
                for arg in [
                    x["list_actions"]
                    for x in self.parser.list_subparsers
                    if x["name"] == current_tab_name
                ]
            ][0]
            self.parser.arguments = current_tab_arguments + self.parser.arguments
            out_args.append(current_tab_name)

        self.__widget_recuperation__()

        for arg in self.parser.arguments:
            if (
                arg["type"] is str
                or arg["type"] is "file_path"
                or arg["type"] is "directory_path"
            ):
                if arg["cli"] != []:
                    out_args.append(arg["cli"])
                out_args.append(self.results[arg["name"]])
            elif arg["type"] is int:
                if arg["cli"] != []:
                    out_args.append(arg["cli"])
                out_args.append(str(self.results[arg["name"]]))
            elif arg["type"] is bool:
                if self.results[arg["name"]]:
                    out_args.append(arg["cli"])
            elif arg["type"] == "append_action":
                for command in self.results[arg["name"]].split(" "):
                    out_args.append(arg["cli"])
                    out_args.append(command)
            elif arg["type"] == "count_action":
                name, count = arg["cli"], self.results[arg["name"]]
                # Keep a correspondance between what user see and reality:
                #  the default for count_action gives a «base» value, to which
                #  is added the number of found flags.
                count -= arg["default"]
                out_args.extend([name] * count)
            elif arg["type"] == "version_action":
                pass  # don't do anything ; version is treated elsewhere
            elif callable(arg["type"]):
                if arg["cli"] != []:
                    out_args.append(arg["cli"])
                out_args.append(
                    arg["type"](self.results[arg["name"]])
                )  # TODO: intercept argparse exception due to arg['type'] to print them in the GUI
            else:
                raise ValueError("Type {} is unhandled".format(arg["type"]))
        print("OUT ARGS:", out_args)
        return list(map(str, out_args))

    def __compute_version(self):
        "If such a parameter exists, retrieve the returned version number"
        self.version_text = ""
        if self._version_argument:
            strout = io.StringIO()
            with contextlib.redirect_stdout(strout):
                try:
                    self.parser.parser.old_parse_args([self._version_argument])
                except SystemExit as err:
                    pass
            self.version_text = strout.getvalue()

    def __widget_for_version(self) -> QLabel or None:
        "If the dedicated parameter exists, retrieve it and show it in a returned label"
        self.__compute_version()
        if self.version_text:
            label = QLabel(self.version_text, parent=self)
            return label

    def parsed_args(self):
        return self.parser.parser.old_parse_args(self.out_args)

    def __create_widgets__(self, parent, arguments):
        """
        Function to generate widgets from arguments list in parent layout.
        In: - parent: QLayout
            - arguments: List of arguments formatted by ExtractedParser object.
        Out: a QWidget is added into the parent layout.
        """
        # Creation of arguments widgets
        for action in arguments:
            if action["type"] == "version_action":
                self._version_argument = action["cli"]
                continue  # don't propose a widget for that here
            widget = widget_for_type(
                action["type"], action["default"], action["choices"]
            )
            widget.setToolTip(action["help"])
            if action["type"] in {"directory_path", "file_path"}:
                path_callback = (
                    QFileDialog.getExistingDirectory
                    if action["type"] == "directory_path"
                    else QFileDialog.getOpenFileName
                )
                # Widget to keep clean the file path
                path_file = QLineEdit(action["default"])
                # Link between path_widget and widget
                def closure(p):
                    widget.clicked.connect(lambda: p.setText(path_callback()[0]))

                closure(path_file)
                # Adding both widgets on the same line
                hbox = QHBoxLayout()
                hbox.addWidget(path_file)
                hbox.addWidget(widget)
                parent.addRow(action["name"], hbox)
            else:
                self._on_widget_creation(widget, action["name"])
                parent.addRow(action["name"], widget)

    def _on_widget_creation(self, widget, option_name):
        "Called for each option widget created ; do nothing ; to be overriden"
        pass

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
        # Each line in GUI's tab is an item for CLI
        for i in range(self.widget_layout.rowCount()):
            item = self.widget_layout.itemAt(i, QFormLayout.FieldRole)
            # 2 cases expected: single widget, or hbox layout
            # If path_file or path_directory
            if item.widget() is None:
                widget = item.layout()
                value = widget.metaObject().userProperty().read(widget)
            # Standard widget case
            elif item.layout() is None:
                widget = item.widget()
                value = widget.metaObject().userProperty().read(widget)
            # None of the expected cases
            else:
                raise ValueError("{}-th widget is {}".format(i, item))
            # Find widget label
            label = self.widget_layout.labelForField(widget).text()
            self.results[label] = value


def widget_for_type(
    wtype: type, default_value: object, choices: iter = None
) -> QWidget:
    """Return initialized widget describing given type with given value"""
    max_int = 2 ** 31 - 1
    if choices is None:
        if wtype is bool:
            widget = QCheckBox()
            try:
                widget.setCheckState(Qt.Checked if default_value else Qt.Unchecked)
            except:
                widget.setCheckState(False)
        elif wtype is "file_path" or wtype is "directory_path":
            widget = QPushButton("...")
        elif wtype is str:
            widget = QLineEdit(default_value)
        elif wtype is int:
            widget = QSpinBox()
            widget.setRange(-max_int, max_int)
            widget.setSingleStep(1)
            widget.setValue(int(default_value or 0))
        elif wtype == "append_action":  # or wtype is argparse._AppendAction:
            widget = QLineEdit(default_value)
        elif wtype == "count_action":
            widget = widget_for_type(int, default_value, choices)
            widget.setRange(
                int(default_value), max_int
            )  # minimal value is already set by default value
        elif callable(wtype):  # probably an user-defined function
            # expect that the type annotation will provide us some info
            fullargs = inspect.getfullargspec(wtype)
            if not fullargs.args:  # no argument
                raise TypeError(
                    "Unhandled type 'custom function {}', because it has no positional argument".format(
                        wtype.__name__
                    )
                )
            atype = inspect.getfullargspec(wtype).annotations.get(
                fullargs.args[0], None
            )
            if atype is None:  # no annotation given, we don't know what to do
                raise TypeError(
                    "Unhandled type 'custom function {}', because it has no indication of output type".format(
                        wtype.__name__
                    )
                )
            return widget_for_type(atype, default_value, choices)
        else:
            raise TypeError("Unhandled type: {}".format(wtype))
    else:  # there is a choice to make  (between strings, it sounds necessary)
        widget = QComboBox()
        widget.addItems(tuple(map(str, choices)))
        widget.setCurrentText(str(default_value))
    return widget

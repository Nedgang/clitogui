"""Definition of an interactive GUI"""

import sys
import inspect
import argparse
from .gui import Interface
from .image_viewer import ImageViewer
from itertools import zip_longest

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
except ImportError:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *


def clear_layout(layout):
    "Remove everything in a given layout"
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            clear_layout(item.layout())
        layout.deleteLater()


class InteractiveInterface(Interface):
    """Automatized GUI using ExtractedParser object, with interactive visualization of outputs

    Overriden methods:
        - __init__: get a callback and few others parameters
        - _build_interface: add an apply button and add the output view
        - _on_accept: keep track of the callback output
        - parsed_args: embeds the callback output into the parsed object

    """

    def __init__(
        self,
        clitogui_actions,
        callback: callable,
        *,
        tabulate: bool = False,
        tab_names: iter = (),
        autorun: bool = True,
        minsize: (int, int) = (300, 300),
    ):
        """Creation of the window, and associated layout

        clitogui_actions -- the ExtractedParser instance
        callback -- the function parsed_args -> results to call whenever necessary
        tabulate -- if output value is a list/tuple, put each value in its tab
        tab_names -- if there is tabs, use the strings in that iterable to name them
        autorun -- if True, will update the output view each time an option is changed
        minsize -- minimal size of the output view

        """
        self.callback, self.tabulate, self.tab_names, self.autorun, self.minsize = (
            callback,
            tabulate,
            tuple(tab_names),
            autorun,
            tuple(map(int, minsize)),
        )
        self.last_callback_output = ()  # nothing to show
        super().__init__(clitogui_actions)

    def _build_interface(self):
        left_layout = super()._build_interface()
        # Add a new button to run the program
        self.apply_button = QPushButton("Run", self)
        self.apply_button.clicked.connect(self.update_view)
        self.apply_button.setDefault(True)  # make it the default button of the gui
        self.buttons.addButton(self.apply_button, QDialogButtonBox.ButtonRole.ApplyRole)

        # Add a new space to print the output
        self.output_view = self.make_new_outview()
        # layouting
        new_main_layout = (
            QHBoxLayout()
        )  # will replace the previous one, to include the output view
        new_main_layout.addLayout(left_layout)
        new_main_layout.addWidget(self.output_view)
        return new_main_layout

    def _on_widget_creation(self, widget, option_name):
        "if autorun, run the callback when a new value has been set"
        if self.autorun:
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(self.update_view)
            elif isinstance(widget, QSpinBox):
                widget.valueChanged.connect(self.update_view)
            elif isinstance(widget, QCheckBox):
                widget.stateChanged.connect(self.update_view)
            elif isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(self.update_view)
            else:
                raise NotImplementedError(
                    "Widget of type {} cannot be triggered on autorun".format(
                        type(widget)
                    )
                )

    def make_new_outview(self):
        output_view = OutputView(self.tabulate, self.tab_names)
        output_view.setMinimumSize(*self.minsize)
        output_view.show_values(self.last_callback_output)
        return output_view

    def parsed_args(self):
        "Return the same object, patched to also embed the final returning values"
        parsed = super().parsed_args()
        if hasattr(parsed, "_output"):
            raise TypeError(
                f"Parser object {self.parser.parser} already has an _output attribute"
            )
        parsed._output = self.last_callback_output
        return parsed

    def _on_accept(self):
        super()._on_accept()
        self.last_callback_output = self.callback(
            super().parsed_args()
        )  # remember the outputs
        if inspect.isgenerator(self.last_callback_output):
            self.last_callback_output = tuple(self.last_callback_output)

    def update_view(self):
        "Parse GUI to get args, call callback with it"
        self._on_accept()  # compute the new output data
        # create the view accordingly
        old_outview = self.layout().takeAt(1).widget()
        old_outview.setParent(None)
        old_outview.deleteLater()
        self.output_view = self.make_new_outview()
        self.layout().addWidget(self.output_view)
        assert self.layout().itemAt(1).widget() is self.output_view


class OutputView(QFrame):
    """Container of widgets showing the outputs of the InteractiveInterface.callback.

    A new instance is created each time the callback is called.

    """

    def __init__(self, tabulate: bool, tab_names: iter):
        super().__init__()
        self.tabulate = tabulate
        self.tab_names = tab_names

    def show_values(self, values: object):
        "Update internal widgets"
        widgets = tuple(widgets_from_values(values, self))
        if self.tabulate and isinstance(values, (list, tuple, set, frozenset, dict)):
            # let's make a tabulated view
            tabs = QTabWidget()
            for idx, (elem, tabname) in enumerate(
                zip_longest(values, self.tab_names), start=1
            ):
                layout = QVBoxLayout()
                for item in widgets_from_values(elem, tabs):
                    layout.addWidget(item)
                frame = QFrame(parent=tabs)
                frame.setLayout(layout)
                tabs.addTab(frame, tabname or f"tab {idx}")
            layout = QVBoxLayout()
            layout.addWidget(tabs)
            self.setLayout(layout)
        else:
            layout = QVBoxLayout()
            for wid in widgets_from_values(values, self):
                layout.addWidget(wid)
            self.setLayout(layout)


def widgets_from_values(obj: object, parent=None) -> [QWidget]:
    if isinstance(obj, tuple):
        # a list of widgets to print in different tabs
        for elem in obj:
            yield from widgets_from_values(elem, parent)
    elif isinstance(obj, list):
        # just a list of objects to print vertically
        frame = QFrame(parent=parent)  # will contain everything
        layout = QVBoxLayout()
        for elem in obj:
            h_layout = QHBoxLayout()
            for wid in widgets_from_values(elem, frame):
                h_layout.addWidget(wid)
            layout.addLayout(h_layout)
        frame.setLayout(layout)
        yield frame
    elif isinstance(obj, str):
        yield QLabel(obj, parent)
    elif Image and isinstance(obj, Image.Image):
        yield ImageViewer(obj, parent=parent)
    else:
        raise NotImplementedError(
            "Output '{}' of type '{}' is currently non implemented".format(
                obj, type(obj)
            )
        )

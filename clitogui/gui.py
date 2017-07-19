#!/usr/bin/python3
"""

"""

##########
# IMPORT #
##########
import os
import tkinter as tk

import argparse

WINDOW_HEIGHT, WINDOW_WIDTH = 800, 600

#########
# CLASS #
#########
class Interface(tk.Frame):
    def __init__(self, parent, clitogui_actions, *args, **kwargs):
        self.parent = parent
        self.parent.geometry("{}x{}".format(WINDOW_HEIGHT, WINDOW_WIDTH))
        self.parent.title("ClitoGui POC") # ADAPTER AU TITRE DU PROGRAMME

        self.actions  = tuple(clitogui_actions)
        self.out_args = [] # Will be populated with args
        self.holders  = {} # value holder of widgets

        # LAUNCH WIDGETS CREATION
        self.__create_widgets()

    def __create_widgets(self):
        """
        Creation of a widget for each action in the parser.
        """
        for idx, action in enumerate(self.actions):
            # print(action)
            # Label each widget with the help text.
            lab = tk.Label(self.parent, text=action.help, width=40)
            lab.grid(row = idx, column = 0)

            if type(action) == argparse._StoreAction:
                type_return = str
                holder = tk.Variable(value = action.default)
                wid = tk.Spinbox(self.parent, textvariable = holder)
            elif type(action) == argparse._StoreTrueAction:
                type_return = bool
                holder = tk.BooleanVar(value = action.default)
                wid = tk.Checkbutton(self.parent, variable = holder)
            else:
                raise TypeError("Unhandled type: {}".format(type(action)))

            wid.grid(row=idx, column=1)

            if action.option_strings == []:
                self.holders[""] = (type_return, holder)
            else:
                self.holders[action.option_strings[0]] = (type_return, holder)

            # Launch button
            tk.Button(self.parent, text="Run!", command=self.run).\
                grid(row=len(self.actions), column = 0, columnspan=2)

    def run(self):
        """
        Return values from the GUI.
        """
        for option, (type_return, holder) in self.holders.items():
            # print(option, type_return, holder.get())
            # Positionnal argument (buggy if more than 1)
            if option == '':
                self.out_args.append(str(holder.get()))
            # Boolean arguments
            elif type_return == bool:
                if holder.get() == True:
                    self.out_args.append(option)
            # Standard arguments
            else:
                self.out_args.append(option)
                self.out_args.append(str(holder.get()))

        # print(self.out_args)
        # Kill the GUI
        self.parent.quit()

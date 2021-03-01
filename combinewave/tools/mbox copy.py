import tkinter
from tkinter import Toplevel
from tkinter.ttk import Label, Button



import tkinter as tk

class CustomDialog(tk.Toplevel):
    def __init__(self, parent, prompt):
        tk.Toplevel.__init__(self, parent)

        self.var = tk.StringVar()

        self.label = tk.Label(self, text=prompt)
        self.entry = tk.Entry(self, textvariable=self.var)
        self.ok_button = tk.Button(self, text="OK", command=self.on_ok)

        self.label.pack(side="top", fill="x")
        self.entry.pack(side="top", fill="x")
        self.ok_button.pack(side="right")

        self.entry.bind("<Return>", self.on_ok)

    def on_ok(self, event=None):
        self.destroy()

    def show(self):
        self.wm_deiconify()
        self.entry.focus_force()
        self.wait_window()
        return self.var.get()


class Mbox(object):

    root = None

    def __init__(self, title):
        """
        msg = <str> the message to be displayed
        """
        self.t = Toplevel()
        # self.slot = slot
        self.t.title(title)
        Label(self.t, text="Plate type").grid(column=0, row=0, padx=10, pady=5)

        btn = Button(self.t, text="OK", command=lambda: self.ok())
        btn.grid(row=3, column=1, pady=20, padx=20)
        btn = Button(self.t, text="Cancel",
                     command=lambda: self.cancel())
        btn.grid(row=3, column=2, pady=20, padx=20)

    def ok(self):
        self.t.destroy()
        return "good"

    def cancel(self):
        self.t.destroy()
        return "cancel"


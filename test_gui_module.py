import tkinter as tk
from chem_robox.tools import custom_widgets
from tkinter import *

root = Tk()


response = custom_widgets.stop_or_resume()
print(response)

root.mainloop()

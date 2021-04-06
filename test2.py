# Importing tkinter module
from tkinter import * 
from tkinter.ttk import *
  
# creating Tk window
master = Tk()
  
# setting geometry of tk window
master.geometry("200x200")
  
# button widget
b1 = Button(master, text = "Click me !")
  
# This is where b1 is placed inside b2 with in_ option
b1.place(relx = 0, rely = 0, anchor = NW)
  
 
# infinite loop which is required to
# run tkinter program infinitely
# until an interrupt occurs
mainloop()
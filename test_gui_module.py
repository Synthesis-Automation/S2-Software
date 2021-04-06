import tkinter as tk
from combinewave.tools import custom_widgets

root = tk.Tk()

root.geometry("300x300+0+0")


reactor_frame = tk.Frame(relief=tk.RAISED, borderwidth=2, width=400, height=400)

# reactor_frame.grid(column=0, row=11, sticky=tk.N)
# # tk.Label(reactor_frame, text="Current reactor").grid(row=0, pady=5)
# reactor_selection_frame = tk.Frame(reactor_frame, relief="ridge", bg="gray")     
# reactor_selection_frame.grid(row=1)
reactor_selection = custom_widgets.Reactor_selection_on_screen(current=0)

# my_frame = tk.Frame(root)
# my_frame.pack()

# new  = custom_widgets.Item_selection_popup(parent= root, title = "Current reactor:  ", slot_list=["A1", "B1", "A2", "B2"], COLS=2, ROWS=2, current=2)
# print(new.get_current())

# new2  = custom_widgets.Reactor_selection_on_screen(parent= root, current=0)

# options=[{"text": "0.5 mL", "value": 0.5}, 
#          {"text": "1.0 mL", "value": 1.0},
#          {"text": "2.0 mL", "value": 2.0},
#         ]
# new  = custom_widgets.Volume_selection(parent= my_frame, title = "Current reactor:  ", options=options)

# connect_btn = tk.Button(text="Print", command=lambda: print_value())
# connect_btn.pack()

# def print_value():
#     print(new.get_value())

# top = tk.Toplevel()
# top.title("new window")

root.mainloop()
import time

import tkinter as tk
from tkinter import ttk
from tkinter.ttk import Button, Label
from combinewave.tools import helper
from combinewave.parameters import CAPPER, LIQUID, TABLET

class Item_selection_on_screen():
    """ give a on screen frame for item selection """

    def __init__(self, parent=None, slot_list=["A1", "B1"], COLS=2, ROWS=1, current=0):
        self.parent = parent
        self.btn_list = []
        self.slot_list = slot_list
        self.current = current
        self.total_number_of_vials = COLS*ROWS
        i = 0
        for col in range(COLS):
            for row in range(ROWS):
                text = self.slot_list[i]
                def action(x=i): return self.click(x)
                btn = tk.Button(self.parent, text=text, width=3,
                                #fg = "skyblue",
                                bg="lightgrey",
                                relief="ridge",
                                border=0,
                                command=action)
                btn.grid(row=row+2, column=col, pady=10, padx=10)
                self.btn_list.append(btn)
                i = i+1
        self.btn_list[self.current].configure(bg="sky blue")

    def click(self, x):
        self.btn_list[self.current].configure(bg="lightgrey")
        self.btn_list[x].configure(bg="sky blue")
        self.current = x

    def get_current(self, format="number"):
        '''return numeric format such as 0, 1 when format = number, else return non-numeric format such as A1'''
        if format == "number":
            return self.current
        else:
            return self.slot_list[self.current]

    def set_current(self, current_item):
        self.current = current_item

    def next(self, next_no=1):
        self.btn_list[self.current].configure(bg="lightgrey")
        self.current = self.current + next_no
        if self.current == self.total_number_of_vials:
            self.current = 0
        self.btn_list[self.current].configure(bg="sky blue")


class Item_selection_popup():
    ''' the module generate a button, which can popup new windows to select a item such as tip'''

    def __init__(self, parent, title="Current Tip:  ", slot_list=["A1", "B1"], COLS=5, ROWS=3, current=0):
        self.parent = parent
        self.slot_list = slot_list
        self.title = title
        self.COLS = COLS
        self.ROWS = ROWS
        self.total_number_of_vials = COLS*ROWS
        self.current = current
        self.item_text = self.title + self.slot_list[self.current]
        self.item_button = tk.Button(self.parent, text=self.item_text, font="Helvetica 11", bg="sky blue",
                                     command=lambda: self.click())
        self.item_button.grid(column=0, row=6, pady=20)
        self.time = float(time.time())

    def click(self):
        (self.current, text) = Button_list(self.parent, title="Select Current Item",
                                           slot_list=self.slot_list, COLS=self.COLS, ROWS=self.ROWS, current=self.current).show()
        self.item_button.configure(text=self.title + text)
        self.time = float(time.time())

    def get_current(self, format="number"):
        '''return numeric format such as 0, 1 when format = number, else return format such as A1'''
        if format == "number":
            return self.current
        else:
            return self.slot_list[self.current]

    def set_current(self, current):
        self.current = current

    def next(self, next_no=1):
        self.current = self.current + next_no
        if self.current == self.total_number_of_vials:
            self.current = 0
            tk.messagebox.showinfo(
                " ", "Warning: All tips were used, please refill tip rack from A1")
        self.item_text = self.title + self.slot_list[self.current]
        self.item_button.configure(text=self.item_text)

    def reset_current(self, current):
        self.current = current
        self.next(0)

    def get_update_time(self):
        return self.time


class Button_list(tk.Toplevel):
    """used internally"""
    def __init__(self, parent, title="", slot_list=[], COLS=1, ROWS=2, current=0):
        tk.Toplevel.__init__(self, parent)
        self.title(title)
        self.configure(bg="gray")
        self.btn_list = []
        self.slot_list = slot_list
        self.current = current
        i = 0
        for col in range(COLS):
            for row in range(ROWS):
                text = self.slot_list[i]
                def action(x=i): return self.click(x)
                btn = tk.Button(self, text=text, width=3,
                                #fg = "skyblue",
                                bg="lightgrey",
                                relief="ridge",
                                border=0,
                                command=action)
                btn.grid(row=row+2, column=col, pady=10, padx=10)
                self.btn_list.append(btn)
                i = i+1
        self.btn_list[self.current].configure(bg="sky blue")
        self.grab_set()  # keep this pop window focused

    def click(self, x):
        self.choice = x
        text = f"x"
        self.btn_list[x].configure(text=text)
        self.destroy()

    def show(self):
        self.wm_deiconify()
        self.btn_list[self.current].focus_force()
        self.wait_window()
        return (self.choice, self.slot_list[(self.choice)])


class Volume_selection():
    """ give a on screen volume inputor on selection """

    def __init__(self, parent=None, title="Reaction volume (mL)", options=[{"text": "0.5 mL", "value": 0.5}]):
        self.parent = parent
        self.options = options
        self.volume_frame = tk.LabelFrame(
            self.parent, text=title, fg="RoyalBlue4", font="Helvetica 11 bold")
        self.volume_frame.grid()
        self.volume = tk.IntVar(None, len(options)-1)
        self.text = ttk.Entry(self.volume_frame, width=15,
                             font=('Helvetica', '11'))
        self.text.grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        for i in range(len(options)):
            tk.Radiobutton(self.volume_frame,
                           text=options[i]["text"], font="Helvetica 11",
                           variable=self.volume,
                           value=i).grid(column=0, row=1+i, pady=2, sticky=tk.W)

    def get_value(self):
        volume_choice = self.volume.get()
        sample_volume = self.options[volume_choice]["value"]
        if self.text.get():
            sample_volume = float(self.text.get())
        return sample_volume


class Information_display():
    """ on screen scrolledtext for display message """

    def __init__(self, parent=None, title="Progress information", width=160, height=15):
        self.parent = parent
        self.display = tk.scrolledtext.ScrolledText(
            self.parent, width=width, height=height)
        self.display.grid()
        self.display.insert(tk.INSERT, title)

    def display_msg(self, msg, start_over=True):
        self.display.configure(state='normal')
        if start_over:
            self.display.delete(1.0, tk.END)
        self.display.insert(tk.INSERT, msg)
        self.display.insert(tk.INSERT, '\n')
        self.display.see("end")
        self.display.update()
        self.display.configure(state='disabled')


# For select of the position of a vial on the deck
class Vial_selection_on_screen():
    """ give a on screen frame for vial selection (both slot and vial) """

    def __init__(self, parent=None, slot_list=["A1", "B1"], vial_list = ["A1", "B1"], current=("C2", "A1")):
        self.parent = parent        
        self.slot_list = [['A1', 'B1', 'C1'], ['A2', 'B2', 'C2'], ['A3', 'B3', 'C3'], ['A4', 'B4', 'C4'], ['A5', 'B5', 'C5']]
        self.vial_list = [['A1', 'B1', 'C1'], ['A2', 'B2', 'C2'], ['A3', 'B3', 'C3'], ['A4', 'B4', 'C4'], ['A5', 'B5', 'C5']]
        self.current = current
        self.btn_list = []
        self.vial_selection = {}
        # self.total_number_of_vials = COLS*ROWS
        col = 0
        row = 0
        for slot_column in self.slot_list:
            for slot in slot_column:
                vial_position = "A1"
                text = self.slot_list[i]+ "\n vial@ "+ self.slot_list[vial_position]
                def action(x=slot): return self.click(x)
                btn = tk.Button(self.parent, text=text, width=8,
                                bg="lightgrey",
                                relief="ridge",
                                border=0,
                                command=action)
                btn.grid(row=row+2, column=col, pady=10, padx=10)
                self.btn_list.append(btn)
                self.vial_selection.update({slot: vial_position})
                row = row + 1
            col = col + 1
        self.btn_list[self.current].configure(bg="sky blue")

    def click(self, slot_no):
        self.btn_list[self.current].configure(bg="lightgrey")
        self.current = slot_no
        btn_list = Button_list(self.parent, title="Select Current Item",
                                           slot_list=["A1", "B1", "A2", "B2"], COLS=2, ROWS=2, current=self.vial_selection[slot_no])
        (self.current, text) = btn_list.show()
        print(self.current, text)
        text = self.slot_list[slot_no]+ "\n vial@ "+ self.vial_selection[slot_no]
        self.btn_list[self.current].configure(bg="sky blue", text = text)
        # self.item_button.configure(text=self.title + text)

    def get_current(self, format="number"):
        '''return numeric format such as 0, 1 when format = number, else return non-numeric format such as A1'''
        if format == "number":
            return self.current
        else:
            return self.slot_list[self.current]



class Move_axes():
    """ An onscreen frame for move all axes """

    def __init__(self, parent=None, robot = None):
        self.parent = parent
        self.robot = robot

        # Head selection (Z1:cpapper, Z2:Tablet, Z3:Liquid)
        Label(self.parent, text="Select head for calibration",
              style="Default.Label").grid(column=0, row=0, pady=5)
        self.head_select = ttk.Combobox(
            self.parent, state="readonly", font=('Helvetica', '11'))
        self.head_select["values"] = (CAPPER, TABLET, LIQUID)
        self.head_select.current(1)  # set the selected item Z2
        self.head_select.grid(column=0, row=1, padx=15, sticky=tk.N)

        ttk.Label(self.parent, text=" Moving distance per-click", style="Default.Label").grid(column=1,
                                                                                              row=0, padx=20, pady=5)
        self.distance = ttk.Combobox(
            self.parent, state="readonly", font=('Helvetica', '11'))
        self.distance["values"] = ("20 mm", "10 mm", "5 mm",
                                   "1 mm", "0.5 mm", "0.2 mm")
        self.distance.current(2)  # set the selected item
        self.distance.grid(column=1, row=1)

        btn_forward = Button(
            self.parent, text="Move to Rear (Y)", style="Green.TButton", command=lambda: self.move_rear())
        btn_forward.grid(column=1, row=13, padx=50, pady=20)

        btn_left = Button(self.parent, text="Move to Left (X)", style="Green.TButton",
                          command=lambda: self.move_left())
        btn_left.grid(column=0, row=14, padx=20, pady=10)

        btn_right = Button(self.parent, text="Move to Right (X)", style="Green.TButton",
                           command=lambda: self.move_right())
        btn_right.grid(column=2, row=14, padx=0, pady=10)

        btn_backward = Button(self.parent, text="Move to Front (Y)", style="Green.TButton",
                              command=lambda: self.move_front())
        btn_backward.grid(column=1, row=15, padx=20, pady=10)

        btn_up_Z1 = Button(self.parent, text=" Z Up ", style="Default.TButton",
                           command=lambda: self.up())
        btn_up_Z1.grid(column=3, row=13, padx=60, pady=30)

        btn_down_Z1 = Button(self.parent, text="Z Down ", style="Default.TButton",
                             command=lambda: self.down())
        btn_down_Z1.grid(column=3, row=15, padx=60, pady=20)
        self.message = Label(self.parent, text="X=    Y=    Z=  ")
        self.message.grid(column=1, row=14)

    def get_current_head(self):
        current_head = self.head_select.get()
        return current_head

    def display_XYZ(self, msg):
        self.message.configure(text=msg)
        # self.update()

    def read_XYZ(self):
        x = self.robot.get_axe_position("x")
        y = self.robot.get_axe_position("y")
        current_Z_axe = self.head_select.get()
        z = self.robot.get_axe_position(current_Z_axe)
        xyz = f"X= {x}  Y= {y}  Z= {z}"
        return xyz

    def move_left(self):
        self.robot.xy_platform.move(
            x=-1*helper.get_float_number(self.distance.get()))
        self.display_XYZ(self.read_XYZ())

    def move_right(self):
        self.robot.xy_platform.move(
            x=helper.get_float_number(self.distance.get()))
        self.display_XYZ(self.read_XYZ())

    def move_rear(self):
        self.robot.xy_platform.move(
            y=-1*helper.get_float_number(self.distance.get()))
        self.display_XYZ(self.read_XYZ())

    def move_front(self):
        self.robot.xy_platform.move(
            y=1*helper.get_float_number(self.distance.get()))
        self.display_XYZ(self.read_XYZ())

    def up(self):
        current_head = self.head_select.get()
        self.robot.z_platform.move(
            head=current_head, z=helper.get_float_number(self.distance.get()))
        self.display_XYZ(self.read_XYZ())

    def down(self):
        current_head = self.head_select.get()
        self.robot.z_platform.move(
            head=current_head, z=-1*helper.get_float_number(self.distance.get()))
        self.display_XYZ(self.read_XYZ())


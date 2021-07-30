import logging
import time

import tkinter as tk
from tkinter import ttk
from tkinter.ttk import Button, Label
from chem_robox.tools import helper
from chem_robox.parameters import CAPPER, LIQUID, TABLET


class Item_selection_on_screen():
    """ give a on screen frame for item selection """

    def __init__(self, parent=None, slot_list=["A1", "B1"], COLS=2, ROWS=1, current=0, show_number=False):
        self.parent = parent
        self.time = float(time.time())
        self.btn_list = []
        self.slot_list = slot_list
        self.current = current
        self.total_number_of_vials = COLS*ROWS
        i = 0
        width = 3
        if show_number:
            width = 6
        for col in range(COLS):
            for row in range(ROWS):
                if show_number:
                    text = self.slot_list[i]+" | "+str(i+1)
                else:
                    text = self.slot_list[i]

                def action(x=i): return self.click(x)
                btn = tk.Button(self.parent, text=text, width=width,
                                # fg = "skyblue",
                                bg="lightgrey",
                                relief="ridge",
                                border=0,
                                command=action)
                btn.grid(row=row+2, column=col, pady=8, padx=8)
                self.btn_list.append(btn)
                i = i+1
        self.btn_list[self.current].configure(bg="sky blue")

    def click(self, x):
        self.btn_list[self.current].configure(bg="lightgrey")
        self.btn_list[x].configure(bg="sky blue")
        self.current = x
        self.time = float(time.time())

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

    def highlight_current(self):
        self.btn_list[self.current].configure(bg="sky blue")

    def un_highlight_current(self):
        self.btn_list[self.current].configure(bg="lightgrey")

    def get_update_time(self):
        return self.time


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
        self.parent = parent
        self.title(title)
        self.configure(bg="gray")
        self.btn_list = []
        self.slot_list = slot_list
        self.current = current
        self.choice = self.current
        i = 0
        for col in range(COLS):
            for row in range(ROWS):
                text = self.slot_list[i]
                def action(x=i): return self.click(x)
                btn = tk.Button(self, text=text, width=3,
                                # fg = "skyblue",
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
        # self.parent.grab_set() # keep its parent window focused
        self.destroy()

    def show(self):
        self.wm_deiconify()
        self.btn_list[self.current].focus_force()
        self.wait_window()
        return (self.choice, self.slot_list[(self.choice)])


class Volume_selection():
    """ give a on screen volume inputor on selection"""

    def __init__(self, parent=None, title="Reaction volume (mL)", options=[{"text": "0.5 mL", "value": 0.5}]):
        self.parent = parent
        self.options = options
        self.volume_frame = tk.LabelFrame(
            self.parent, text=title, fg="RoyalBlue4", font="Helvetica 11 bold")
        self.volume_frame.grid()
        # text input entry
        self.text = ttk.Entry(self.volume_frame, width=20,
                              font=('Helvetica', '11'))
        self.text.grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        # option
        self.volume = tk.IntVar(None, len(options)-2)
        for i in range(len(options)):
            ttk.Radiobutton(self.volume_frame,
                            text=options[i]["text"],
                            variable=self.volume,
                            value=i).grid(column=0, row=1+i, pady=2, sticky=tk.W)

    def get_value(self):
        volume_choice = self.volume.get()
        sample_volume = self.options[volume_choice]["value"]
        if self.text.get():
            sample_volume = float(self.text.get())
        return sample_volume


class Volume_entry():
    """ give a on screen volume entry box"""

    def __init__(self, parent=None, title="Volume (mL)"):
        self.parent = parent
        self.volume_frame = tk.LabelFrame(
            self.parent, text=title, fg="RoyalBlue4", font="Helvetica 11 bold")
        self.volume_frame.grid()
        # text input entry
        self.text = ttk.Entry(self.volume_frame, width=20,
                              font=('Helvetica', '11'))
        self.text.grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)

    def get(self):
        volume_string = self.text.get()
        if helper.is_float(volume_string):
            return float(volume_string)
        else:
            return False


class Information_display():
    """ on screen scrolledtext for display message """

    def __init__(self, parent=None, width=160, height=15):
        self.parent = parent
        self.display = tk.scrolledtext.ScrolledText(
            self.parent, width=width, height=height)
        self.display.grid()

    def clear(self):
        self.display.configure(state='normal')
        self.display.delete(1.0, tk.END)
        self.display.configure(state='disabled')

    def display_msg(self, msg, start_over=True, save_to_log=True):
        self.display.configure(state='normal')
        if start_over:
            self.display.delete(1.0, tk.END)
        self.display.insert(tk.INSERT, msg)
        self.display.insert(tk.INSERT, '\n')
        self.display.see("end")
        self.display.update()
        self.display.configure(state='disabled')
        if save_to_log:
            logging.info(msg)


class Move_axes():
    """ An onscreen frame for move all axes """

    def __init__(self, parent=None, robot=None):
        self.parent = parent
        self.robot = robot

        # Head selection (Z1:cpapper, Z2:Tablet, Z3:Liquid)
        Label(self.parent, text="Select Head ",
              style="Default.Label").grid(column=0, row=0, pady=5)
        self.head_select = ttk.Combobox(
            self.parent, state="readonly", font=('Helvetica', '11'))
        self.head_select["values"] = (CAPPER, TABLET, LIQUID)
        self.head_select.current(2)  # set the selected item Z2
        self.head_select.grid(column=0, row=1, padx=15, sticky=tk.N)

        ttk.Label(self.parent, text=" Moving distance per-click",
                  style="Default.Label").grid(column=1, row=0, padx=20, pady=5)
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


# Reactor or other plate selection
class Plate_on_screen():
    """ give a on screen frame for selection of reactors """

    def __init__(self, parent=None, title="Current reactor", show_number=False, image_file="", plate_type="reactor_12p", current=0):
        self.parent = parent
        self.plate_type = plate_type
        if self.plate_type == "reactor_27p":
            self.item_list = [{'name': 'A1', 'x': 0.5, 'y': 0.09999999999999998}, {'name': 'A2', 'x': 0.6530833333333333, 'y': 0.13044444444444447}, {'name': 'A3', 'x': 0.7828333333333333, 'y': 0.21716666666666667}, {'name': 'A4', 'x': 0.8695555555555555, 'y': 0.34691666666666665}, {'name': 'A5', 'x': 0.9, 'y': 0.5}, {'name': 'A6', 'x': 0.8695555555555555, 'y': 0.6530833333333333}, {'name': 'A7', 'x': 0.7828333333333333, 'y': 0.7828333333333333}, {'name': 'A8', 'x': 0.6530833333333333, 'y': 0.8695555555555555}, {'name': 'A9', 'x': 0.5, 'y': 0.9}, {'name': 'A10', 'x': 0.34691666666666665, 'y': 0.8695555555555555}, {'name': 'A11', 'x': 0.21716666666666667, 'y': 0.7828333333333333}, {'name': 'A12', 'x': 0.13044444444444447, 'y': 0.6530833333333333}, {'name': 'A13', 'x': 0.09999999999999998, 'y': 0.5}, {
                'name': 'A14', 'x': 0.13044444444444447, 'y': 0.34691666666666665}, {'name': 'A15', 'x': 0.21716666666666667, 'y': 0.21716666666666667}, {'name': 'A16', 'x': 0.34691666666666665, 'y': 0.13044444444444447}, {'name': 'B1', 'x': 0.5, 'y': 0.25}, {'name': 'B2', 'x': 0.6469444444444444, 'y': 0.29774999999999996}, {'name': 'B3', 'x': 0.7377777777777778, 'y': 0.42275}, {'name': 'B4', 'x': 0.7377777777777778, 'y': 0.57725}, {'name': 'B5', 'x': 0.6469444444444444, 'y': 0.70225}, {'name': 'B6', 'x': 0.5, 'y': 0.75}, {'name': 'B7', 'x': 0.35305555555555557, 'y': 0.70225}, {'name': 'B8', 'x': 0.26222222222222225, 'y': 0.57725}, {'name': 'B9', 'x': 0.26222222222222225, 'y': 0.42275}, {'name': 'B10', 'x': 0.35305555555555557, 'y': 0.29774999999999996}, {'name': 'C1', 'x': 0.5, 'y': 0.5}]
        elif self.plate_type == "reactor_12p":
            self.item_list = [{'name': 'A1', 'x': 0.2153846153846154, 'y': 0.25384615384615383}, {'name': 'B1', 'x': 0.2153846153846154, 'y': 0.4423076923076923}, {'name': 'C1', 'x': 0.2153846153846154, 'y': 0.6307692307692307}, {'name': 'A2', 'x': 0.4, 'y': 0.25384615384615383}, {'name': 'B2', 'x': 0.4, 'y': 0.4423076923076923}, {'name': 'C2', 'x': 0.4, 'y': 0.6307692307692307}, {
                'name': 'A3', 'x': 0.5846153846153846, 'y': 0.25384615384615383}, {'name': 'B3', 'x': 0.5846153846153846, 'y': 0.4423076923076923}, {'name': 'C3', 'x': 0.5846153846153846, 'y': 0.6307692307692307}, {'name': 'A4', 'x': 0.7692307692307693, 'y': 0.25384615384615383}, {'name': 'B4', 'x': 0.7692307692307693, 'y': 0.4423076923076923}, {'name': 'C4', 'x': 0.7692307692307693, 'y': 0.6307692307692307}]
        elif self.plate_type == "reactor_circle_8mL_20p":
            self.item_list = [{'name': 'A1', 'x': 0.5689411764705883, 'y': 0.10899999999999999}, {'name': 'A2', 'x': 0.6985294117647058, 'y': 0.15611764705882353}, {'name': 'A3', 'x': 0.8041764705882353, 'y': 0.24476470588235294}, {'name': 'A4', 'x': 0.8731176470588236, 'y': 0.3641764705882353}, {'name': 'A5', 'x': 0.8970588235294117, 'y': 0.5}, {'name': 'A6', 'x': 0.8731176470588236, 'y': 0.6358235294117647}, {'name': 'A7', 'x': 0.8041764705882353, 'y': 0.755235294117647}, {'name': 'A8', 'x': 0.6985294117647058, 'y': 0.8438823529411765}, {'name': 'A9', 'x': 0.5689411764705883, 'y': 0.891}, {'name': 'A10', 'x': 0.43105882352941177, 'y': 0.891}, {'name': 'A11', 'x': 0.30147058823529416, 'y': 0.8438823529411765}, {'name': 'A12', 'x': 0.19582352941176467, 'y': 0.755235294117647}, {'name': 'A13', 'x': 0.12688235294117645, 'y': 0.6358235294117647}, {'name': 'A14', 'x': 0.10294117647058826, 'y': 0.5}, {'name': 'A15', 'x': 0.12688235294117645, 'y': 0.3641764705882353}, {
                'name': 'A16', 'x': 0.19582352941176467, 'y': 0.24476470588235294}, {'name': 'A17', 'x': 0.30147058823529416, 'y': 0.15611764705882353}, {'name': 'A18', 'x': 0.43105882352941177, 'y': 0.10899999999999999}, {'name': 'A19', 'x': 0.4329411764705882, 'y': 0.5}, {'name': 'A20', 'x': 0.5670588235294117, 'y': 0.5}]
        elif self.plate_type == "reactor_circle_8mL_10p":
            self.item_list = [{'name': 'A1', 'x': 0.5925882352941176, 'y': 0.21094117647058824}, {'name': 'A2', 'x': 0.7043529411764706, 'y': 0.29211764705882354}, {'name': 'A3', 'x': 0.7470588235294118, 'y': 0.42352941176470593}, {'name': 'A4', 'x': 0.7043529411764706, 'y': 0.5549411764705883}, {'name': 'A5', 'x': 0.5925882352941176, 'y': 0.6361176470588236}, {'name': 'A6', 'x': 0.45447058823529407, 'y': 0.6361176470588236}, {
                'name': 'A7', 'x': 0.3427058823529412,                                                                                                                                                                                                                                                                              'y': 0.5549411764705883}, {'name': 'A8', 'x': 0.3, 'y': 0.42352941176470593}, {'name': 'A9', 'x': 0.3427058823529412, 'y': 0.29211764705882354}, {'name': 'A10', 'x': 0.45447058823529407, 'y': 0.21094117647058824}]
        elif self.plate_type == "reactor_square_8mL_20p":
            self.item_list = [{'name': 'A1', 'x': 0.16821428571428573, 'y': 0.2915714285714286}, {'name': 'A2', 'x': 0.33249999999999996, 'y': 0.2915714285714286}, {'name': 'A3', 'x': 0.4967857142857143, 'y': 0.2915714285714286}, {'name': 'A4', 'x': 0.6610714285714285, 'y': 0.2915714285714286}, {'name': 'A5', 'x': 0.8253571428571428, 'y': 0.2915714285714286}, {'name': 'B1', 'x': 0.08607142857142858, 'y': 0.4338571428571429}, {'name': 'B2', 'x': 0.25035714285714283, 'y': 0.4338571428571429}, {'name': 'B3', 'x': 0.41464285714285715, 'y': 0.4338571428571429}, {'name': 'B4', 'x': 0.5789285714285715, 'y': 0.4338571428571429}, {'name': 'B5', 'x': 0.7432142857142857, 'y': 0.4338571428571429}, {
                'name': 'C1', 'x': 0.16821428571428573, 'y': 0.5761428571428572}, {'name': 'C2', 'x': 0.33249999999999996, 'y': 0.5761428571428572}, {'name': 'C3', 'x': 0.4967857142857143, 'y': 0.5761428571428572}, {'name': 'C4', 'x': 0.6610714285714285, 'y': 0.5761428571428572}, {'name': 'C5', 'x': 0.8253571428571428, 'y': 0.5761428571428572}, {'name': 'D1', 'x': 0.08607142857142858, 'y': 0.7184285714285716}, {'name': 'D2', 'x': 0.25035714285714283, 'y': 0.7184285714285716}, {'name': 'D3', 'x': 0.41464285714285715, 'y': 0.7184285714285716}, {'name': 'D4', 'x': 0.5789285714285715, 'y': 0.7184285714285716}, {'name': 'D5', 'x': 0.7432142857142857, 'y': 0.7184285714285716}]
        elif self.plate_type == "plate_GC_LC_2mL":
            self.item_list = [{'name': 'A1', 'x': 0.09158571428571428, 'y': 0.3271428571428572}, {'name': 'A2', 'x': 0.2558714285714286, 'y': 0.3271428571428572}, {'name': 'A3', 'x': 0.4201571428571429, 'y': 0.3271428571428572}, {'name': 'A4', 'x': 0.5844428571428572, 'y': 0.3271428571428572}, {'name': 'A5', 'x': 0.7487285714285714, 'y': 0.3271428571428572}, {'name': 'B1', 'x': 0.09158571428571428, 'y': 0.46941428571428573}, {'name': 'B2', 'x': 0.2558714285714286, 'y': 0.46941428571428573}, {'name': 'B3', 'x': 0.4201571428571429, 'y': 0.46941428571428573}, {'name': 'B4', 'x': 0.5844428571428572, 'y': 0.46941428571428573}, {'name': 'B5', 'x': 0.7487285714285714, 'y': 0.46941428571428573}, {'name': 'C1', 'x': 0.09158571428571428, 'y': 0.6116857142857143}, {'name': 'C2', 'x': 0.2558714285714286, 'y': 0.6116857142857143}, {'name':
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               'C3', 'x': 0.4201571428571429, 'y': 0.6116857142857143}, {'name': 'C4', 'x': 0.5844428571428572, 'y': 0.6116857142857143}, {'name': 'C5', 'x': 0.7487285714285714, 'y': 0.6116857142857143}, {'name': 'D1', 'x': 0.09158571428571428, 'y': 0.753957142857143}, {'name': 'D2', 'x': 0.2558714285714286, 'y': 0.753957142857143}, {'name': 'D3', 'x': 0.4201571428571429, 'y': 0.753957142857143}, {'name': 'D4', 'x': 0.5844428571428572, 'y': 0.753957142857143}, {'name': 'D5', 'x': 0.7487285714285714, 'y': 0.753957142857143}]
        else:
            self.item_list = [{'name': 'A1', 'x': 0.16821428571428573, 'y': 0.2915714285714286}, {'name': 'B1', 'x': 0.08607142857142858, 'y': 0.4338571428571429}, {'name': 'C1', 'x': 0.16821428571428573, 'y': 0.5761428571428572}, {'name': 'D1', 'x': 0.08607142857142858, 'y': 0.7184285714285716}, {'name': 'A2', 'x': 0.33249999999999996, 'y': 0.2915714285714286}, {'name': 'B2', 'x': 0.25035714285714283, 'y': 0.4338571428571429}, {'name': 'C2', 'x': 0.33249999999999996, 'y': 0.5761428571428572}, {'name': 'D2', 'x': 0.25035714285714283, 'y': 0.7184285714285716}, {'name': 'A3', 'x': 0.4967857142857143, 'y': 0.2915714285714286}, {'name': 'B3', 'x': 0.41464285714285715, 'y': 0.4338571428571429}, {
                'name': 'C3', 'x': 0.4967857142857143, 'y': 0.5761428571428572}, {'name': 'D3', 'x': 0.41464285714285715, 'y': 0.7184285714285716}, {'name': 'A4', 'x': 0.6610714285714285, 'y': 0.2915714285714286}, {'name': 'B4', 'x': 0.5789285714285715, 'y': 0.4338571428571429}, {'name': 'C4', 'x': 0.6610714285714285, 'y': 0.5761428571428572}, {'name': 'D4', 'x': 0.5789285714285715, 'y': 0.7184285714285716}, {'name': 'A5', 'x': 0.8253571428571428, 'y': 0.2915714285714286}, {'name': 'B5', 'x': 0.7432142857142857, 'y': 0.4338571428571429}, {'name': 'C5', 'x': 0.8253571428571428, 'y': 0.5761428571428572}, {'name': 'D5', 'x': 0.7432142857142857, 'y': 0.7184285714285716}]

        tk.Label(self.parent, text=title, fg="RoyalBlue4",
                 font="Helvetica 11 bold").place(relx=0.35, rely=0, anchor=tk.NW)
        if image_file != "":
            canvas = tk.Canvas(self.parent, width=90, height=20)
            canvas.place(relx=0.3, rely=0.10, anchor=tk.NW)
            self.img = tk.PhotoImage(file="./images/" + image_file)
            canvas.create_image(1, 1, anchor=tk.NW, image=self.img)

        self.btn_list = []
        self.current = current
        self.total = len(self.item_list)
        for i in range(self.total):
            if show_number:
                text = self.item_list[i]["name"] + " | "+str(i+1)
                width = 5
            else:
                text = self.item_list[i]["name"]
                width = 3

            def action(x=i): return self.click(x)

            btn = tk.Button(self.parent, text=text, width=width,
                            bg="lightgrey",
                            relief="ridge",
                            border=0,
                            command=action)
            btn.place(relx=self.item_list[i]['x'],
                      rely=self.item_list[i]['y'], anchor=tk.NW)
            self.btn_list.append(btn)
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
            return self.item_list[self.current]["name"]

    def set_current(self, current_item):
        self.un_highlight_current()
        self.current = current_item
        self.highlight_current()

    def next(self, next_no=1):
        self.btn_list[self.current].configure(bg="lightgrey")
        self.current = self.current + next_no
        if self.current == self.total:
            self.current = 0
        self.btn_list[self.current].configure(bg="sky blue")

    def highlight_current(self):
        self.btn_list[self.current].configure(bg="sky blue")

    def un_highlight_current(self):
        self.btn_list[self.current].configure(bg="lightgrey")


# Multiple liquids selection
class Multiple_reagents():
    """ give a frame for Multiple liquids selection """

    def __init__(self, parent=None, chem_synthesis=None, reagent_type="liquid", liquids=[{"title": "Quench solution: ", "reagents": (("NaCl-water"))}]):
        # liquid_1="Quench solution: ", liquid_2="", reagents_1=("NaCl-water"), reagents_2=("Ether")):
        self.parent = parent
        self.chem_synthesis = chem_synthesis
        self.solvent_frame = tk.Frame(self.parent)
        self.solvent_frame.grid(column=0, row=0, sticky=tk.N)
        self.solvent_selection_list = []
        self.volume_entry_list = []
        self.number_of_liquids = len(liquids)
        if reagent_type == "liquid":
            title = "Volume (mL): "
            default_amount = "1.0"
        else:
            title = "Amount (mmol): "
            default_amount = "0.005"
        for j in range(self.number_of_liquids):
            i = j*10
            Label(self.solvent_frame, text=" ").grid(row=i, sticky=tk.W)
            Label(self.solvent_frame, style="Default.Label",
                  text=liquids[j]["title"]).grid(row=i+1, column=0, sticky=tk.E)
            solvent_selection = ttk.Combobox(
                self.solvent_frame, font=('Helvetica', '11'), width=15)
            solvent_selection["values"] = liquids[j]["reagents"]
            solvent_selection.current(0)
            solvent_selection.grid(row=i+1, column=1, pady=5, sticky=tk.W)
            Label(self.solvent_frame, style="Default.Label",
                  text=title).grid(row=i+2, column=0, sticky=tk.E)
            volume_entry = ttk.Entry(self.solvent_frame, width=17,
                                     font=('Helvetica', '11'))
            volume_entry.grid(row=i+2, column=1, pady=2, sticky=tk.W)
            Label(self.solvent_frame, text=" ").grid(row=i+4, sticky=tk.W)
            volume_entry.insert(tk.END, default_amount)
            self.solvent_selection_list.append(solvent_selection)
            self.volume_entry_list.append(volume_entry)

    def get_reagents(self):
        liquids = []
        for i in range(self.number_of_liquids):
            solvent_volume_string = self.volume_entry_list[i].get()
            solvent_name = self.solvent_selection_list[i].get()
            if solvent_name == "":
                continue
            if not helper.is_float(solvent_volume_string):
                tk.messagebox.showinfo(
                    " ", "Please enter solvent volume in mL!")
                return []
            solvent_volume = float(solvent_volume_string)
            solvent_info = self.chem_synthesis.locate_reagent(solvent_name)
            if "not found" in solvent_info:
                tk.messagebox.showinfo(" ", solvent_info)
                return []
            else:
                plate_name = solvent_info["plate"]
                position = solvent_info["vial"]
                reagent_type = solvent_info["type"]
                mmol_per_tablet = solvent_info["amount"]
                is_volatile = solvent_info["is_volatile"]

            liquids.append({"name": solvent_name, "plate": plate_name,
                            "position": position, "type": reagent_type, "amount": solvent_volume, "mmol_per_tablet": mmol_per_tablet, "is_volatile": is_volatile})
        if liquids == []:
            tk.messagebox.showinfo(
                "Attention", "Please enter a valid solvent name and volume!")
        return(liquids)


class Dialog_box(ttk.Frame):
    def __init__(self,  title="Attention", msg="Operation paused.", button_1="Resume", button_2="Stop"):
        self.popup_window = tk.Toplevel()
        self.popup_window.title(title)
        self.popup_window.resizable(False, False)
        ttk.Label(self.popup_window, text=msg, style="Default.Label").grid(
            column=0, row=1, columnspan=2, padx=10, pady=10)
        self.return_msg = "resume"
        # Save buttons
        self.button_1 = Button(self.popup_window, text=button_1, style="Green.TButton",
                               command=lambda: self.button_click_1())
        self.button_1.grid(column=0, row=2, padx=20, pady=10)

        self.button_2 = Button(self.popup_window, text=button_2, style="Red.TButton",
                               command=lambda: self.button_click_2())
        self.button_2.grid(column=1, row=2, padx=20, pady=10)
        self.popup_window.protocol("WM_DELETE_WINDOW", self.do_nothing())
        self.button_1.focus_force()
        self.popup_window.grab_set()
        self.popup_window.wait_window()

    def do_nothing(self):
        pass

    def button_click_1(self):
        self.return_msg = "resume"
        self.popup_window.destroy()

    def button_click_2(self):
        self.return_msg = "stop"
        self.popup_window.destroy()


# Below are functions
# ask for stop / resume option during operation
def stop_or_resume():
    my_box = Dialog_box()
    return my_box.return_msg

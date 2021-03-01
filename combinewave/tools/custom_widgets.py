import tkinter as tk
from tkinter import ttk
import time


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
        self.text = tk.Entry(self.volume_frame, width=15,
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
    """ scrolledtext for display message """

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



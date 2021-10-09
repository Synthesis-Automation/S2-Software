# coding:utf-8
import time
import math
import socket
import threading
import logging
import random
import os
from pathlib import Path
from datetime import datetime

import tkinter as tk
from tkinter import ttk
from tkinter import Menu, Canvas, PhotoImage, Toplevel, filedialog, scrolledtext, messagebox
from tkinter.ttk import Notebook, Label, Button

from chem_robox.robot import robot
from chem_robox.chemical_synthesis import synthesis
from chem_robox.tools import custom_widgets
# CAPPER = 'Z3'...
from chem_robox.parameters import CAPPER, LIQUID, TABLET, VERSION, SYSTEM_NAME, NEW_PLAN_HEADER


class Main(tk.Tk):
    def __init__(self):
        super().__init__()
        self.iconbitmap(self, default=Path("./images/flash.ico"))
        self.title(SYSTEM_NAME)

        # Main menu
        self.menu = Menu(self, bg="lightgrey", fg="black")

        self.file_menu = Menu(self.menu, tearoff=0)
        self.file_menu.add_command(label="Open reagent index",
                                   command=lambda: self.synthesis_tab.open_reagent_index())
        self.file_menu.add_separator()
        self.file_menu.add_separator()

        self.file_menu.add_command(label="New synthesis plan",
                                   command=lambda: self.synthesis_tab.new_plan())
        self.file_menu.add_command(label="Open synthesis plan",
                                   command=lambda: self.synthesis_tab.open_plan())
        self.file_menu.add_command(label="Save synthesis plan",
                                   command=lambda: self.synthesis_tab.save_plan())
        self.file_menu.add_command(label="Save synthesis plan as new file",
                                   command=lambda: self.synthesis_tab.save_as_plan())
        self.file_menu.add_separator()
        self.file_menu.add_separator()

        self.file_menu.add_command(label="Open synthesis plan in excel format",
                                   command=lambda: self.synthesis_tab.open_plan_excel())
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.exit_gui)
        self.menu.add_cascade(label="File ", menu=self.file_menu)

        self.log_menu = Menu(self.menu, tearoff=0)
        self.log_menu.add_command(
            label="Open log book", command=lambda: self.open_log_book())
        self.log_menu.add_command(
            label="Empty log book", command=lambda: self.empty_log_book())
        self.log_menu.add_separator()
        self.log_menu.add_command(
            label="Open log book folder", command=lambda: self.open_log_book_folder())
        self.menu.add_cascade(label="LogBook ", menu=self.log_menu)

        self.calibration_menu = Menu(self.menu, tearoff=0)
        self.calibration_menu.add_command(
            label="Plate Calibration", command=lambda: self.plate_calibration())
        self.calibration_menu.add_command(
            label="Tip Calibration", command=lambda: self.tip_calibration())
        self.calibration_menu.add_command(
            label="Reference Point Calibration", command=lambda: self.reference_calibration())
        self.menu.add_cascade(label="Calibration ", menu=self.calibration_menu)

        self.Manual_control_menu = Menu(self.menu, tearoff=0)
        self.Manual_control_menu.add_command(
            label="Manual control", command=lambda: self.manual_control())
        self.Manual_control_menu.add_command(
            label="Return to safe position", command=lambda: chem_robot.go_home())

        self.menu.add_cascade(label="Manual-Control  ",
                              menu=self.Manual_control_menu)

        self.Liquid_distrubution_menu = Menu(self.menu, tearoff=0)
        self.Liquid_distrubution_menu.add_command(
            label="Quech and Extraction", command=lambda: self.quech_and_extraction())
        self.Liquid_distrubution_menu.add_command(
            label="Transfer Liquid to Reactor", command=lambda: self.solvent_distrubution())
        self.Liquid_distrubution_menu.add_command(
            label="Transfer Solid to Reactor", command=lambda: self.solid_distrubution())
        self.menu.add_cascade(
            label="Chemistry ", menu=self.Liquid_distrubution_menu)

        self.cap_operation_menu = Menu(self.menu, tearoff=0)
        self.cap_operation_menu.add_command(
            label="Cap reactors", command=lambda: self.cap_reactor())
        self.cap_operation_menu.add_command(
            label="Decap reactors", command=lambda: self.decap_reactor())
        self.menu.add_cascade(label="Capper ", menu=self.cap_operation_menu)

        helpmenu = Menu(self.menu, tearoff=0)
        helpmenu.add_command(label="About", command=lambda: self.about())
        self.menu.add_cascade(label="Help", menu=helpmenu)

        tk.Tk.config(self, menu=self.menu)
        # End of main menu

        # Notebook tab
        self.notebook = Notebook(self, style='lefttab.TNotebook')

        connect_tab = Connect_tab(self.notebook)
        self.connect_img = PhotoImage(file=Path("./images/connect_t.png"))
        self.notebook.add(connect_tab, text="Connect  Robot\n",
                          image=self.connect_img, compound=tk.TOP)

        self.deck_tab = Deck_tab(self.notebook)
        self.deck_img = PhotoImage(file=Path("./images/deck_t.png"))
        self.notebook.add(self.deck_tab, text="Deck & Reactor\n",
                          image=self.deck_img, compound=tk.TOP)

        self.tip_tab = Tip_tab(self.notebook)
        self.tip_img = PhotoImage(
            file=Path("./images/tips.png"))
        self.notebook.add(
            self.tip_tab, text="Tips Selection\n", image=self.tip_img, compound=tk.TOP)

        self.synthesis_tab = Synthesis_tab(
            self.notebook, tip_selection=self.tip_tab)
        self.synthesis_img = PhotoImage(file=Path("./images/synthesis_t.png"))
        self.notebook.add(self.synthesis_tab, text="Synthesis setup\n",
                          image=self.synthesis_img, compound=tk.TOP)

        self.monitor_tab = Monitor_tab(
            self.notebook, tip_selection=self.tip_tab)
        self.monitor_img = PhotoImage(file=Path("./images/monitor.png"))
        self.notebook.add(self.monitor_tab, text="Reaction Monitor\n",
                          image=self.monitor_img, compound=tk.TOP)

        self.workup_tab = Workup_tab(self.notebook, tip_selection=self.tip_tab)
        self.workup_img = PhotoImage(file=Path("./images/workup.png"))
        self.notebook.add(self.workup_tab, text="Reaction Workup\n",
                          image=self.workup_img, compound=tk.TOP)

        self.notebook.bind("<ButtonRelease-1>", self.update_tip_by_tab_clicked)
        self.notebook.pack(fill=tk.BOTH, expand=1)
        # End of Notebook tab setup

        # Save tip position before exit main program
        self.protocol("WM_DELETE_WINDOW", self.exit_gui)

    def about(self):
        messagebox.showinfo(" ", SYSTEM_NAME + " " + VERSION)

    def quech_and_extraction(self):
        liquids = [{"title": "Quench solution: ", "reagents": ("NaCl-water", "K2CO3-water", "NaHCO3-water", "NH4Cl-water", "")},
                   {"title": "Extraction solvent: ", "reagents": ("MeOtBu", "Ethyl-acetate", "Hexanes", "Toluene", "Ether", "DCM", "")}]
        popup = Liquid_distrubution(
            tip_selection=self.tip_tab, liquids=liquids, title="Quench and extract reaction")
        self.wait_window(popup.popup_window)

    def solvent_distrubution(self):
        liquids = [{"title": "Liquid name: ", "reagents": (
            "Ethyl-acetate", "Hexanes", "Toluene", "Ether", "DCM", "THF", "Acetone", "Dioxane", "DCE")}]
        popup = Liquid_distrubution(
            tip_selection=self.tip_tab, liquids=liquids, title="Add liquid")
        self.wait_window(popup.popup_window)

    def solid_distrubution(self):
        reagents = [{"title": "Solid name: ", "reagents": (
            "KF", "K2CO3")}]
        popup = Solid_distrubution(title="Add solid ", reagents=reagents)
        self.wait_window(popup.popup_window)

    def manual_control(self):
        popup = Manual_control(tip_selector=self.tip_tab.tip_selector)
        self.wait_window(popup.popup_window)

    def cap_reactor(self):
        popup = Cap_operation(option="Cap reactors")
        self.wait_window(popup.popup_window)

    def decap_reactor(self):
        popup = Cap_operation(option="Decap reactors")
        self.wait_window(popup.popup_window)

    def plate_calibration(self):
        popup = Plate_calibration()
        self.wait_window(popup.popup_window)

    def tip_calibration(self):
        popup = Tip_calibration()
        self.wait_window(popup.popup_window)

    def reference_calibration(self):
        popup = Reference_calibration()
        self.wait_window(popup.popup_window)

    def update_tip_by_tab_clicked(self, event=None):
        # Make sure that all tip selection have the same current tip number
        self.synthesis_tab.reactor_update()
        self.workup_tab.reactor_update()
        self.monitor_tab.reactor_update()

    def open_log_book(self):
        os.startfile(logbook_filename)

    def open_log_book_folder(self):
        path = os.path.realpath(logbook_folder)
        os.startfile(path)

    def empty_log_book(self):
        yes = messagebox.askyesno(
            "Info", "Are you sure to empty log book?")
        if yes:
            with open(logbook_filename, 'w'):
                pass
        else:
            return

    def exit_gui(self):
        self.tip_tab.save()
        self.destroy()


class Connect_tab(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)

        Label(self, text=" ").pack()
        Label(self, text="Wellcome to\n" + SYSTEM_NAME,
              style="Title.Label").pack(pady=10)
        canvas = Canvas(self, width=800, height=400)
        canvas.pack(pady=10)
        self.img = PhotoImage(file="./images/flash.png")
        canvas.create_image(1, 1, anchor=tk.NW, image=self.img)
        self.connect_btn = Button(self, text="Connect and home robot", style="Green.TButton",
                                  command=lambda: self.run_thread())
        self.connect_btn.pack(pady=20)
        self.status = tk.Label(
            self, text="Robot Status: Not connected", fg="red", width=50)
        self.status.pack(side=tk.BOTTOM,  fill=tk.X)

    def connect(self, ask_before_homing=False):
        try:
            if not chem_robot.ready:
                if not chem_robot.is_connected:
                    chem_robot.connect()
                    chem_robot.home_all_z()
                    chem_robot.is_connected = True
                if ask_before_homing:
                    yes = messagebox.askyesno(
                        "Info", "Make sure it is safe to home robot, proceed?")
                    if not yes:
                        return False
                # chem_robot.green_light("on")
                chem_robot.home_xy()
                chem_robot.move_to(head=TABLET, vial=(
                    "A3", "A1"), use_allow_list=False)
                chem_robot.gripper.initialization()
                chem_robot.pipette.initialization()
                chem_robot.ready = True
            self.status.configure(text="Robot Status: Ready",
                                  fg="green")
            self.connect_btn["state"] = "disabled"
        except Exception:
            messagebox.showinfo(
                " ", "Connection failed, please \n1) check your USB connection; \n2) make sure that powder is on. \nAnd try again.")

    def run_thread(self):
        t = threading.Thread(target=self.connect)
        t.start()


class Deck_tab(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        Label(self, text="Deck Setup", style="Title.Label").grid(
            column=0, row=0, padx=50, pady=10, columnspan=5)
        self.slot_list = chem_robot.deck.get_slot_list()
        self.btn_list = []
        self.config = []
        i = 0
        for plate_sn in chem_robot.deck.deck_config.values():
            slot = self.slot_list[i]
            plate_type = plate_sn["plate"].split(':')[0]
            plate_no = plate_sn["plate"].split(':')[1]
            assignment = chem_robot.deck.deck_config[slot]["assignment"]
            self.config.append({"slot": slot, "plate_type": plate_type,
                                "plate_no": plate_no, "assignment": assignment})
            i = i+1
            # do not use the R1, R2, R3
            if i >= 15:
                break
        COLS = 5
        ROWS = 3
        i = 0
        self.deck_frame = tk.LabelFrame(
            self, text="  Deck  ", fg="RoyalBlue4", font="Helvetica 11 bold")
        self.deck_frame.grid(column=0, columnspan=5, row=10,
                             padx=20, pady=10, sticky=tk.W)
        for row in range(ROWS):
            for col in range(COLS):
                slot = self.config[i]["slot"]
                plate_type = self.config[i]["plate_type"]
                plate_no = self.config[i]["plate_no"]
                assignment = self.config[i]["assignment"]
                text = f"{slot}\n{plate_type} : {plate_no}\n{assignment}"
                def action(x=i): return self.slot_assignment(x)
                btn = Button(
                    self.deck_frame, text=text, style="Plate.TButton", command=action)
                if assignment in ["Tips 50uL", "Tips 1000uL"]:
                    btn.configure(style="Plate_r.TButton")
                if assignment in ["Reactor", "Trash", "Clean up"]:
                    btn["state"] = "disabled"
                btn.grid(row=row+2, column=col, pady=15, padx=10)
                self.btn_list.append(btn)
                i = i+1

        # reactor selection
        self.reactor_list = chem_robot.robot_config["reactor_list"]
        self.reactor_discription = chem_robot.robot_config["reactor_discription"]
        numbers_of_reactors = len(self.reactor_discription)
        current_reactor_name = chem_robot.deck.deck_config["C3"]["plate"].split(':')[
            0]
        current_reactor_id = self.reactor_list.index(current_reactor_name)
        self.reactor_frame = tk.LabelFrame(
            self, text=" Select Reactor ", fg="RoyalBlue4", font="Helvetica 11 bold")
        self.reactor_frame.grid(column=0, columnspan=5, row=20,
                                padx=20, pady=20, sticky=tk.W)
        self.reactor_selection = tk.IntVar(None, numbers_of_reactors-1)
        for reactor_id in range(numbers_of_reactors):
            ttk.Radiobutton(self.reactor_frame,
                            text=self.reactor_discription[reactor_id],
                            variable=self.reactor_selection,
                            value=reactor_id,
                            command=lambda: self.save_reactor(),
                            ).grid(column=reactor_id, row=50, padx=20, pady=2, sticky=tk.W)
        self.reactor_selection.set(current_reactor_id)

        canvas_list = []
        self.imgs = []
        for reactor_id in range(numbers_of_reactors):
            # image file name:  reactor_name.png
            file_name = self.reactor_list[reactor_id]+".png"
            my_canvas = Canvas(self.reactor_frame, width=210, height=210)
            my_canvas.grid(column=reactor_id, row=60, sticky=tk.W)
            img = PhotoImage(file="./images/" + file_name)
            self.imgs.append(img)
            my_canvas.create_image(1, 1, anchor=tk.NW, image=img)
            canvas_list.append(my_canvas)

    def save_reactor(self):
        current_reactor_id = self.reactor_selection.get()
        reactor_slot = "C3"
        chem_robot.deck.deck_config[reactor_slot] = {
            "plate": self.reactor_list[current_reactor_id]+":001", "assignment": "Reactor"}
        chem_robot.deck.save_deck_config(chem_robot.deck.deck_config)
        chem_robot.deck.reset_current_reactor()

    def slot_assignment(self, x):
        popup = Slot_assignment(self.config[x])
        self.wait_window(popup.t)
        self.config = []
        i = 0
        for plate_sn in chem_robot.deck.deck_config.values():
            slot = self.slot_list[i]
            plate_type = plate_sn["plate"].split(':')[0]
            plate_no = plate_sn["plate"].split(':')[1]
            assignment = chem_robot.deck.deck_config[slot]["assignment"]
            self.config.append({"slot": slot, "plate_type": plate_type,
                                "plate_no": plate_no, "assignment": assignment})
            i = i+1
            if i >= 15:
                break
        slot = self.config[x]["slot"]
        plate_type = self.config[x]["plate_type"]
        plate_no = self.config[x]["plate_no"]
        assignmnent = self.config[x]["assignment"]
        text = f"{slot}\n{plate_type} : {plate_no}\n{assignmnent}"
        self.btn_list[x].configure(text=text)


class Slot_assignment():
    def __init__(self, slot):
        self.t = Toplevel()
        self.slots = slot
        self.t.title(slot["slot"])
        Label(self.t, text="Plate type").grid(column=0, row=0, padx=10, pady=5)
        Label(self.t, text="Plate serial No.").grid(
            column=1, row=0, padx=10, pady=5)

        self.plate_type = ttk.Combobox(self.t, width=15, state="readonly")
        plate_type_turple = ("not_used", "plate_2mL", "plate_5mL", "plate_10mL", "plate_50mL", "tiprack_50uL",
                             "tiprack_1000uL", "plate_GC_LC_2mL", "workup_8mL_20p", "workup_small", "caps")
        self.plate_type["values"] = plate_type_turple
        current = plate_type_turple.index(slot["plate_type"])
        self.plate_type.current(current)  # set the selected item
        self.plate_type.grid(column=0, row=2, padx=10, pady=5)

        self.plate_serial = ttk.Combobox(self.t, state="readonly")
        plate_serial_turple = ("001", "002", "003", "004", "005", "006", "007",
                               "008", "009", "010")
        self.plate_serial["values"] = plate_serial_turple
        current = plate_serial_turple.index(slot["plate_no"])
        self.plate_serial.current(current)
        self.plate_serial.grid(column=1, row=2, padx=10, pady=5)

        save_btn = Button(self.t, text="Save", command=lambda: self.save())
        save_btn.grid(row=3, column=0, pady=20, padx=20)
        cancel_btn = Button(self.t, text="Cancel",
                            command=lambda: self.cancel())
        cancel_btn.grid(row=3, column=1, pady=20, padx=20)
        save_btn.focus_force()
        self.t.grab_set()  # keep this pop window focused

    def save(self):
        plate_type = self.plate_type.get()
        plate_no = self.plate_serial.get()
        plate_name = plate_type + ":" + plate_no
        assignment_dict = chem_robot.deck.robot_config["assignments"]
        assignment = assignment_dict[plate_type]
        slot = self.slots["slot"]
        chem_robot.deck.deck_config[slot] = {
            "plate": plate_name, "assignment": assignment}
        chem_robot.deck.save_deck_config(chem_robot.deck.deck_config)
        self.t.destroy()

    def cancel(self):
        self.t.destroy()


class Tip_tab(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        Label(self, text="Tip Selection", style="Title.Label").grid(
            column=0, row=0, padx=50, pady=10, columnspan=2)

        # Tip selector
        self.tip_frame = tk.Frame(self)
        self.tip_frame.grid(column=0, row=11, padx=20, sticky=tk.W)
        Label(self.tip_frame, text="Select current tip (1000 uL)",
              style="Default.Label").grid(row=0, pady=5)

        # show picture of tip rack
        canvas = Canvas(self.tip_frame, width=220, height=200)
        canvas.grid(column=0, row=1, padx=10, pady=10)
        self.img = PhotoImage(file="./images/tips_rack.png")
        canvas.create_image(1, 1, anchor=tk.NW, image=self.img)

        slot_list = chem_robot.deck.get_vial_list_by_plate_type(
            plate_type="tiprack_1000uL")
        col_row = chem_robot.deck.get_cols_rows_by_plate_type(
            plate_type="tiprack_1000uL")
        self.tip_selection_frame = tk.Frame(
            self.tip_frame, relief="ridge", bg="gray")
        self.tip_selection_frame.grid(row=2)
        self.current_tip = chem_robot.deck.get_current_tip(
            tip_type="tips_1000uL")
        self.tip_selector = custom_widgets.Item_selection_on_screen(
            parent=self.tip_selection_frame, slot_list=slot_list, COLS=col_row["columns"], ROWS=col_row["rows"], current=self.current_tip)

        # Tip selector (samll tip)
        self.tip_frame_s = tk.Frame(self)
        self.tip_frame_s.grid(column=1, row=11, padx=20, sticky=tk.W)
        Label(self.tip_frame_s, text="Select current tip (50 uL)",
              style="Default.Label").grid(row=0, pady=5)

        canvas_s = Canvas(self.tip_frame_s, width=220, height=200)
        canvas_s.grid(column=0, row=1, padx=10, pady=10)
        self.img_small = PhotoImage(file="./images/tips_rack_small.png")
        canvas_s.create_image(1, 1, anchor=tk.NW, image=self.img_small)

        self.tip_selection_frame_small = tk.Frame(
            self.tip_frame_s, relief="ridge", bg="LemonChiffon4")
        self.tip_selection_frame_small.grid(row=2)
        self.current_tip_small = chem_robot.deck.get_current_tip(
            tip_type="tips_50uL")
        self.tip_selector_small = custom_widgets.Item_selection_on_screen(
            parent=self.tip_selection_frame_small, slot_list=slot_list, COLS=col_row["columns"], ROWS=col_row["rows"], current=self.current_tip_small)
        self.set_current_tip_type(tip_type="tips_1000uL")

    def save(self):
        tip_type = "tips_1000uL"
        chem_robot.deck.set_current_tip(
            self.tip_selector.get_current(), tip_type=tip_type)
        chem_robot.deck.save_current_tip(tip_type=tip_type)
        tip_type = "tips_50uL"
        chem_robot.deck.set_current_tip(
            self.tip_selector_small.get_current(), tip_type=tip_type)
        chem_robot.deck.save_current_tip(tip_type=tip_type)

    def set_current_tip_type(self, tip_type="tips_1000uL"):
        if tip_type == "tips_1000uL":
            self.current_tip_selector = self.tip_selector
        if tip_type == "tips_50uL":
            self.current_tip_selector = self.tip_selector_small

    def get_current(self, *args, **kwargs):
        return self.current_tip_selector.get_current(*args, **kwargs)

    def next(self, *args, **kwargs):
        self.current_tip_selector.next(*args, **kwargs)
        self.save()
        if self.current_tip_selector.get_current() == 0:
            messagebox.showinfo(
                "Warning ", "All tips are used, please change or refill tip plate!")


class Synthesis_tab(ttk.Frame):

    def __init__(self, parent, tip_selection=None):
        ttk.Frame.__init__(self, parent)
        self.tip_selection = tip_selection
        # title
        Label(self, text=" Reaction Setup ", style="Title.Label").grid(
            column=0, columnspan=4, row=0, padx=20, pady=5)

        ip_address = socket.gethostbyname(socket.gethostname())
        Label(self, text="Enter your reaction protocol below, you may also upload your protocol via IP address: " +
              ip_address, style="Default.Label").grid(column=0, columnspan=4, row=1, padx=15, pady=5, sticky=tk.W)

        # Reaction plan editor
        self.plan_box = scrolledtext.ScrolledText(self, width=150, height=12)
        self.plan_box.grid(column=0, rowspan=4, padx=15, columnspan=4, row=3)
        self.display_plan(NEW_PLAN_HEADER)
        self.is_excel = False
        self.plan_file_name = ""

        # Project name:
        self.project_name_label = Label(
            self, style="Blue.Label", text="Project file name:  "+"not named yet")
        self.project_name_label.grid(row=10, column=0, padx=25, sticky=tk.W)

        # Additional solvent option
        self.solvent_frame = tk.Frame(self)
        self.solvent_frame.grid(column=0, row=11, padx=15, sticky=tk.N)

        Label(self.solvent_frame, text=" ").grid(row=0, sticky=tk.W)
        self.solvent_addition_last = tk.IntVar()
        ttk.Checkbutton(self.solvent_frame, text="Optimize addition squence to save time and tips",
                        variable=self.solvent_addition_last).grid(row=2, sticky=tk.W)
        self.reactor_no_capping = tk.IntVar()
        ttk.Checkbutton(self.solvent_frame, text="Not cap the reactor after finish",
                        variable=self.reactor_no_capping).grid(row=1, sticky=tk.W)

        # Reactor selection
        self.reactor_selection_frame = tk.Frame(
            self, width=300, height=260)
        self.reactor_selection_frame.grid(column=1, row=10, rowspan=3)
        self.current_reactor = chem_robot.deck.get_current_reactor()
        self.reactor_selection = custom_widgets.Plate_on_screen(
            parent=self.reactor_selection_frame, plate_type=self.current_reactor, current=0)

        # cap selection
        self.cap_selection = tk.Frame(
            self, width=300, height=260)
        self.cap_selection.grid(column=2, row=10, rowspan=3)
        self.cap_selection = custom_widgets.Plate_on_screen(
            parent=self.cap_selection, title="Cap plate", plate_type="reactor_square_8mL_20p")

        # Display information
        self.display_frame = tk.LabelFrame(
            self, text="Progress and information")
        self.display_frame.grid(column=0, rowspan=6, columnspan=4,
                                row=20, padx=15, pady=10)
        self.information = custom_widgets.Information_display(
            self.display_frame, width=150, height=14)

        # Parse, run and stop buttons
        self.parse_button = Button(
            self, text="Check reaction protocol", style="Green.TButton", command=lambda: self.parse())
        self.parse_button.grid(column=1, row=30, pady=10)
        self.run_button = Button(
            self, text="Setup reactions", style="Green.TButton", command=lambda: self.run_thread())
        self.run_button.grid(column=2, row=30, pady=10)
        self.stop_button = Button(
            self, text="Pause / Stop", style="Red.TButton", command=lambda: self.stop_reaction())
        self.stop_button.grid(column=3, row=30, pady=10)
        self.run_button["state"] = "disabled"

    def reactor_update(self):
        current_reactor = chem_robot.deck.get_current_reactor()
        if current_reactor != self.current_reactor:
            self.reactor_selection_frame.destroy()
            self.reactor_selection_frame = tk.Frame(
                self, width=300, height=260)
            self.reactor_selection_frame.grid(column=1, row=11)
            self.reactor_selection = custom_widgets.Plate_on_screen(
                parent=self.reactor_selection_frame, plate_type=current_reactor,  current=0)
            self.current_reactor = current_reactor

    def setup(self, tip=0, simulation=False):
        # internal function to run the main sequence
        def run_main_sequence(reaction_list):
            i = 1
            self.reactor_selection.set_current(reactor_start_number)
            for reaction in reaction_list:  # each entry is a reaction as dict
                tracking_number = reaction["tracking_number"]
                output_msg = f"Reaction No. {i} of {number_of_reaction}, (tracking number: {tracking_number})"
                self.information.display_msg(output_msg, start_over=False)
                i = i+1
                reactor_no = self.reactor_selection.get_current(format="A1")
                reactor_vial = (reactor_plate, reactor_no)
                reagent_list = reaction["reagents"]
                for reagent in reagent_list:
                    reagent_type = reagent["type"]
                    reagent_name = reagent["name"]
                    reagent_plate = chem_robot.deck.get_slot_from_plate_name(
                        reagent["plate"])
                    reagent_location = reagent["position"]
                    reagent_vial = (reagent_plate, reagent_location)
                    reagent_amount = reagent["amount"]
                    if reagent_type in ["pure_liquid", "solution"]:
                        reagent_unit = "mL"
                    else:
                        reagent_unit = "tablet"
                    output_msg = f'Transfer {reagent_name} ({reagent_type}, {reagent_amount} {reagent_unit}) from vial@ ({reagent_plate}, {reagent_location}), to reactor@ {reactor_no} ...'
                    self.information.display_msg(output_msg, start_over=False)
                    if not simulation:
                        if reagent_type == "pure_liquid" or reagent_type == "solution":

                            while not chem_robot.decap(reagent_vial):
                                retry = messagebox.askyesno(
                                    "Infomation", "Cap can't be opened, retry?")
                                if not retry:
                                    return "stop"
                            is_volatile = reagent["is_volatile"]
                            # tip selection
                            if reagent_amount > 0.05:
                                tip_type = "tips_1000uL"
                                tip_plate = chem_robot.deck.get_plate_assignment(
                                    "Tips 1000uL")
                                self.tip_selection.set_current_tip_type(
                                    tip_type)
                                tip_no = self.tip_selection.get_current(
                                    format="A1")
                                tip = (tip_plate, tip_no)
                            elif reagent_amount <= 0.05:
                                tip_type = "tips_50uL"
                                tip_plate = chem_robot.deck.get_plate_assignment(
                                    "Tips 50uL")
                                self.tip_selection.set_current_tip_type(
                                    tip_type)
                                tip_no = self.tip_selection.get_current(
                                    format="A1")
                                tip = (tip_plate, tip_no)

                            if chem_robot.transfer_liquid(vial_from=reagent_vial, vial_to=reactor_vial, tip_type=tip_type,
                                                          tip=tip, trash=trash, volume=reagent_amount, is_volatile=is_volatile) == "stop":
                                return "stop"
                            if chem_robot.check_stop_status() == "stop":
                                return "stop"
                            chem_robot.recap(reagent_vial)
                            if chem_robot.check_stop_status() == "stop":
                                return "stop"
                            if not simulation:
                                self.tip_selection.next()

                        if reagent_type == "solid":
                            while not chem_robot.decap(reagent_vial):
                                retry = messagebox.askyesno(
                                    "Infomation", "Cap can't be opened, retry?")
                                if not retry:
                                    return "stop"
                            if chem_robot.check_stop_status() == "stop":
                                return "stop"
                            chem_robot.transfer_tablet(vial_from=reagent_vial, vial_to=reactor_vial,
                                                       number_of_tablet=reagent_amount)
                            if chem_robot.check_stop_status() == "stop":
                                return "stop"
                            chem_robot.recap(reagent_vial)
                            if chem_robot.check_stop_status() == "stop":
                                return "stop"
                            clean_up_position = chem_robot.deck.convert_number_to_A1(
                                random.randint(1, 600), plate=clean_up_plate)
                            chem_robot.clean_up_needle(
                                (clean_up_plate, clean_up_position))
                            if chem_robot.check_stop_status() == "stop":
                                return "stop"
                    else:
                        time.sleep(0.05)

                # skip capping if reactor No cap box is checked
                if reactor_no_cap == 0 and saver_mode == 0:
                    cap_no = self.cap_selection.get_current(format="A1")
                    if chem_robot.check_stop_status() == "stop":
                        return "stop"
                    output_msg = f"Add cap to reactor@ {reactor_vial[1]}"
                    self.information.display_msg(output_msg, start_over=False)
                    if not simulation:
                        chem_robot.pickup_cap((cap_plate, cap_no))
                        self.cap_selection.next()
                    if chem_robot.check_stop_status() == "stop":
                        return "stop"
                    if not simulation:
                        chem_robot.recap(reactor_vial)
                    if chem_robot.check_stop_status() == "stop":
                        return "stop"
                self.information.display_msg(" ", start_over=False)
                self.reactor_selection.next()

        # Internal funciton to add common reagent at the begining or end

        def add_common_reagents(reaction_list):
            i = 0
            for reaction in reaction_list:
                reagent_type = reaction_list[i][0]["type"]
                reagent_name = reaction_list[i][0]["name"]
                reagent_plate = reaction_list[i][0]["plate"]
                reagent_plate = chem_robot.deck.get_slot_from_plate_name(
                    reagent_plate)
                reagent_location = reaction_list[i][0]["position"]
                reagent_vial = (reagent_plate, reagent_location)
                i = i+1
                if not simulation:
                    while not chem_robot.decap(reagent_vial):
                        retry = messagebox.askyesno(
                            "Information", "Cap can't be opened, retry?")
                        if not retry:
                            return "stop"
                self.reactor_selection.set_current(reactor_start_number)
                reagent_counter = 1
                for reagent in reaction:
                    reactor_no = self.reactor_selection.get_current(
                        format="A1")
                    reactor_vial = (reactor_plate, reactor_no)
                    is_volatile = reagent["is_volatile"]
                    reagent_amount = reagent["amount"]
                    if reagent_type in ["pure_liquid", "solution"]:
                        reagent_unit = "mL"
                    else:
                        reagent_unit = "tablet"
                    output_msg = f'Transfer {reagent_name} ({reagent_type}, {reagent_amount} {reagent_unit}) from vial@ ({reagent_plate}, {reagent_location}) to reactor@ {reactor_no}'
                    self.information.display_msg(output_msg, start_over=False)
                    if not simulation:
                        if reagent_type == "pure_liquid" or reagent_type == "solution":
                            # tip selection
                            if reagent_amount > 0.05:
                                tip_type = "tips_1000uL"
                                tip_plate = chem_robot.deck.get_plate_assignment(
                                    "Tips 1000uL")
                                self.tip_selection.set_current_tip_type(
                                    tip_type)
                                tip_no = self.tip_selection.get_current(
                                    format="A1")
                                tip = (tip_plate, tip_no)
                            elif reagent_amount <= 0.05:
                                tip_type = "tips_50uL"
                                tip_plate = chem_robot.deck.get_plate_assignment(
                                    "Tips 50uL")
                                self.tip_selection.set_current_tip_type(
                                    tip_type)
                                tip_no = self.tip_selection.get_current(
                                    format="A1")
                                tip = (tip_plate, tip_no)
                            if reagent_counter <= 1:
                                if not simulation:
                                    chem_robot.pickup_tip(
                                        tip, tip_type=tip_type)
                                    self.tip_selection.next()
                            if reagent_counter > 1:
                                is_volatile = False
                            reagent_counter = reagent_counter + 1
                            print("reagent_counter2",
                                  reagent_counter, is_volatile)
                            if chem_robot.transfer_liquid(vial_from=reagent_vial, vial_to=reactor_vial, tip_type=tip_type,
                                                          tip=None, volume=reagent_amount, is_volatile=is_volatile) == "stop":
                                return "stop"
                            if chem_robot.check_stop_status() == "stop":
                                return "stop"
                        if reagent_type == "solid":
                            if chem_robot.check_stop_status() == "stop":
                                return "stop"
                            chem_robot.transfer_tablet(vial_from=reagent_vial, vial_to=reactor_vial,
                                                       number_of_tablet=reagent_amount)
                            if chem_robot.check_stop_status() == "stop":
                                return "stop"
                    else:
                        time.sleep(0.05)
                    self.reactor_selection.next()
                if reagent_type == "solid":
                    if chem_robot.check_stop_status() == "stop":
                        return
                    clean_up_position = chem_robot.deck.convert_number_to_A1(
                        random.randint(1, 600), plate=clean_up_plate)
                    if not simulation:
                        chem_robot.clean_up_needle(
                            (clean_up_plate, clean_up_position))
                    if chem_robot.check_stop_status() == "stop":
                        return "stop"
                else:
                    if chem_robot.check_stop_status() == "stop":
                        return "stop"
                    if not simulation:
                        chem_robot.drop_tip(vial=trash)
                if not simulation:
                    chem_robot.recap(reagent_vial)

        # start main reaction setup process
        reactions = chem_synthesis.synthesis_plan_json
        if "Error" in reactions:
            print("Error")
            return
        number_of_reaction = len(reactions)
        chem_robot.set_stop_flag(stop=False)
        self.information.clear()
        if not chem_robot.ready:
            simulation = True
        self.run_button["state"] = "disabled"
        if not simulation:
            chem_robot.pipette.initialization()
        reactor_no_cap = self.reactor_no_capping.get()
        saver_mode = self.solvent_addition_last.get()

        if not simulation:
            if messagebox.askokcancel(
                    "Warning", f"Are all reactor vials uncapped?\n") != True:
                return

            if messagebox.askokcancel(
                    "Warning", f"\n Are all reagent vials capped and secured in the plate?") != True:
                return

            if messagebox.askokcancel(
                    "Warning", f"Are enough caps on cap plate?") != True:
                return

        missing = chem_robot.deck.check_missing_assignment(required_plates=[
                                                           "Reagent", "Tips 1000uL", "Trash", "Clean up", "Reaction caps"])
        if missing != "complete":
            retry = messagebox.askyesno(
                "Warning", f"Warning: No {missing} plate is assigned, continue?.")
            if not retry:
                return
        if not simulation:
            self.information.display_msg(
                "Start running...........................................................................")
        else:
            self.information.display_msg(
                "Simulation mode （模拟运行模式）..........................................................")

        cap_plate = chem_robot.deck.get_plate_assignment("Reaction caps")
        reactor_plate = chem_robot.deck.get_current_reactor_slot()
        reactor_start = self.reactor_selection.get_current(format="A1")
        reactor_start_number = self.reactor_selection.get_current()
        cap_start_number = self.cap_selection.get_current()
        trash_plate = chem_robot.deck.get_plate_assignment("Trash")
        trash = (trash_plate, 'A1')
        clean_up_plate = chem_robot.deck.get_plate_assignment("Clean up")

        # Run reaction sequence
        if not saver_mode:
            run_main_sequence(reactions)
        else:
            chem_synthesis.parse_plan_to_json()
            plan = chem_synthesis.convert_plan_to_saver_mode()
            first = plan["first"]
            main_sequence = plan["main"]
            last = plan["last"]
            self.information.display_msg(
                "Running in the saver mode （节省模式启动）", start_over=False)
            self.information.display_msg(
                "Starting to add common reagents (开始添加每个反应的相同试剂)", start_over=False)
            if add_common_reagents(first) == "stop":
                return
            self.information.display_msg("", start_over=False)
            self.information.display_msg(
                "Starting the main sequence (开始主反应序列)", start_over=False)
            if run_main_sequence(main_sequence) == "stop":
                return
            self.information.display_msg(
                "Starting to add remaining common reagents (开始添加尚未加入的相同试剂)", start_over=False)
            if add_common_reagents(last) == "stop":
                return

            # adding cap
            if reactor_no_cap == 0:
                # self.reactor_selection.un_highlight_current()
                self.information.display_msg("", start_over=False)
                if not self.reactor_no_capping.get():
                    self.information.display_msg(
                        "Reagents addition completed, start to cap reactors (试剂添加完成！开始反应瓶加盖操作)", start_over=False)
                    reactor_no = reactor_start
                    self.reactor_selection.set_current(reactor_start_number)
                    # self.reactor_selection.highlight_current()
                    i = 0
                    for i in range(number_of_reaction):
                        reactor_no = self.reactor_selection.get_current(
                            format="A1")
                        reactor_vial = (reactor_plate, reactor_no)

                        message = f"Run {i+1} of {number_of_reaction}, adding cap to reactor at {reactor_vial[1]}"
                        self.information.display_msg(message, start_over=False)
                        cap_no = self.cap_selection.get_current(format="A1")
                        self.cap_selection.next()

                        if chem_robot.check_stop_status() == "stop":
                            return
                        if not simulation:
                            chem_robot.pickup_cap((cap_plate, cap_no))

                        if chem_robot.check_stop_status() == "stop":
                            return
                        if not simulation:
                            chem_robot.recap(reactor_vial)
                        self.reactor_selection.next()

        self.run_button["state"] = "normal"
        self.information.display_msg(
            "*Finished*\n", start_over=False)
        # self.run_button["state"] = "enabled"
        if chem_robot.check_stop_status() == "stop":
            return
        if not simulation:
            chem_robot.go_home()
        if simulation:
            self.reactor_selection.set_current(reactor_start_number)
            self.cap_selection.set_current(cap_start_number)

    def run_thread(self):
        if chem_synthesis.ready:
            t = threading.Thread(target=self.setup)
            t.start()
        else:
            self.information.display_msg("Please load your reaction protocol.")

    def stop_reaction(self):
        chem_robot.set_stop_flag(stop=True)
        self.information.display_msg("Paused ......\n", start_over=False)

    def display_plan(self, msg):
        self.plan_box.delete(1.0, tk.END)
        self.plan_box.insert(tk.INSERT, msg)
        self.plan_box.see("end")

    def open_reagent_index(self):
        filename = filedialog.askopenfilename(title="Select protocol file", filetypes=(
            ("excel file", "*.xlsx"), ("all files", "*.*")))
        print(filename)
        if filename:
            chem_synthesis.load_reagent_index(Path(filename))

    def open_plan(self):
        filename = filedialog.askopenfilename(title="Select protocol file", filetypes=(
            ("txt files", "*.txt"), ("all files", "*.*")))
        plan = open(filename, "r")
        string = plan.read()
        self.plan_file_name = filename
        self.display_plan(string)
        project_name = os.path.basename(self.plan_file_name)
        self.project_name_label["text"] = "Project file name:  " + project_name
        chem_synthesis.ready = True
        self.plan_file_name = filename
        self.is_excel = False

    def new_plan(self):
        filename = filedialog.asksaveasfilename(title="Name your plan file", filetypes=(
            ("txt files", "*.txt"), ("all files", "*.*")))
        if filename == "":
            return
        if ".txt" in filename:
            self.plan_file_name = filename
        else:
            self.plan_file_name = filename + ".txt"
        project_name = os.path.basename(self.plan_file_name)
        self.project_name_label["text"] = "Project file name:  " + project_name
        self.display_plan(NEW_PLAN_HEADER)
        # chem_synthesis.ready = True
        # self.run_button["state"] = "normal"
        self.is_excel = False

    def save_plan(self):
        self.parse()

    def save_as_plan(self):
        filename = filedialog.asksaveasfilename(title="Name your plan file", filetypes=(
            ("txt files", "*.txt"), ("all files", "*.*")))
        if filename == "":
            return
        if ".txt" in filename:
            self.plan_file_name = filename
        else:
            self.plan_file_name = filename + ".txt"
        chem_synthesis.ready = True
        # self.update()
        self.is_excel = False
        project_name = os.path.basename(self.plan_file_name)

        self.project_name_label["text"] = "Project file name:  " + project_name
        self.save_plan()

    def open_plan_excel(self):
        filename = filedialog.askopenfilename(title="Select protocol file", filetypes=(
            ("excel file", "*.xlsx"), ("all files", "*.*")))
        self.display_plan("Plan excel loaded")
        chem_synthesis.ready = True
        # self.run_button["state"] = "normal"
        self.update()
        self.plan_file_name = filename
        self.is_excel = True
        project_name = os.path.basename(self.plan_file_name)
        self.project_name_label["text"] = "Project file name:  " + project_name

    def parse(self):
        if self.plan_file_name == "":
            self.new_plan()
        if self.plan_file_name == "":
            return
        if not self.is_excel:
            self.plan_txt = self.plan_box.get("1.0", tk.END)
            with open(self.plan_file_name, 'w') as output:
                output.write(self.plan_txt)
            chem_synthesis.load_synthesis_plan(self.plan_file_name)
            res = chem_synthesis.parse_plan_to_json()
            if "not found" in res or "Error" in res:
                messagebox.showinfo(" ", res)
                return
        else:
            chem_synthesis.load_synthesis_plan_excel(self.plan_file_name)
            res = chem_synthesis.parse_plan_to_json()
            if "not found" in res:
                messagebox.showinfo(" ", res)
                return
        chem_synthesis.ready = True
        self.setup(simulation=True)
        msg = "Synthesis plan was parsed successfully! All reagents have been located."
        required_plate_list = chem_synthesis.get_required_reagent_plate()
        required_plate_text = "Required plates: " + \
            ", ".join(required_plate_list) + "\n"
        unassigned_plate_list = chem_robot.deck.is_plate_on_deck(
            required_plate_list)
        unassigned_plate_text = "Warning: unassigned plates: " + \
            ", ".join(unassigned_plate_list) + "\n"
        self.information.display_msg(msg, start_over=False)
        self.information.display_msg(required_plate_text, start_over=False)
        if unassigned_plate_list:
            self.information.display_msg(
                unassigned_plate_text, start_over=False)
            self.run_button["state"] = "disabled"
        end_msg = "End of simulation..................................................................\n"
        self.information.display_msg(end_msg, start_over=False)


class Monitor_tab(ttk.Frame):
    def __init__(self, parent, tip_selection=None):
        ttk.Frame.__init__(self, parent)
        self.tip_selection = tip_selection
        # Title
        Label(self, text=" Reaction Monitor ", style="Title.Label").grid(
            column=0, columnspan=4, row=0, padx=20, pady=5)

        # Reactor selection
        self.reactor_selection_frame = tk.Frame(
            self, width=300, height=260)
        self.reactor_selection_frame.grid(column=0, row=11, rowspan=2)
        self.current_reactor = chem_robot.deck.get_current_reactor()
        self.reactor_selection = custom_widgets.Plate_on_screen(
            parent=self.reactor_selection_frame, plate_type=self.current_reactor,  current=0)

        # show picture of operation
        canvas = Canvas(self, width=174, height=130)
        canvas.grid(column=1, row=11, rowspan=2, padx=10, pady=10)
        self.img = PhotoImage(file="./images/monitor_direction.png")
        canvas.create_image(1, 1, anchor=tk.NW, image=self.img)

        # GC-LC vial selector
        self.GC_LC_selection = tk.Frame(
            self, width=300, height=260)
        self.GC_LC_selection.grid(column=2, row=12, rowspan=3)
        self.GC_LC_selection = custom_widgets.Plate_on_screen(
            parent=self.GC_LC_selection, title="GC_LC vial plate", plate_type="plate_GC_LC_2mL")

        # Decap option, reactor_decap.get() = True or False
        self.reactor_decap = tk.IntVar()
        ttk.Checkbutton(self, text="Remove cap of reactor before sampling",
                        variable=self.reactor_decap).grid(column=0, row=15, padx=80, sticky=tk.SW)

        # Number of reactions selection
        self.number_frame = tk.LabelFrame(
            self, text="Number of reactions", fg="RoyalBlue4", font="Helvetica 11 bold")
        self.number_frame.grid(column=0, row=16, padx=80, pady=5, sticky=tk.NW)
        self.number_reaction = ttk.Combobox(
            self.number_frame, state="readonly", font=('Helvetica', '11'))
        self.number_reaction["values"] = tuple(range(1, 21))
        self.number_reaction.current(0)  # set the selected item
        self.number_reaction.grid(pady=5)

        # Sampling volume selector
        options = [{"text": "2 uL", "value": 2.0},
                   {"text": "5 uL", "value": 5.0},
                   {"text": "10 uL", "value": 10.0}
                   ]
        self.sampling_volume_frame = tk.Frame(self, relief="ridge", bg="gray")
        self.sampling_volume_frame.grid(
            column=1, row=15, rowspan=2, sticky=tk.NW)
        self.sampling_volume_selection = custom_widgets.Volume_selection(
            parent=self.sampling_volume_frame, title="Sampling volume (uL)", options=options)

        # Solvent type selection
        self.solvent_frame = tk.LabelFrame(
            self, text="Solvent for dilution", fg="RoyalBlue4", font="Helvetica 11 bold")
        self.solvent_frame.grid(column=2, row=15, pady=5, sticky=tk.NW)
        self.solvent_selection = ttk.Combobox(
            self.solvent_frame, font=('Helvetica', '11'))
        self.solvent_selection["values"] = ("MeOH", "CH3CN",
                                            "DCM", "Ethyl-acetate", "Hexanes")
        self.solvent_selection.current(0)  # set the selected item
        self.solvent_selection.grid(pady=5)

        # Dilution solvent volume selection
        options = [{"text": "0.6 mL", "value": 0.6},
                   {"text": "0.8 mL", "value": 0.8},
                   {"text": "1.0 mL", "value": 1.0}
                   ]
        self.dilution_volume_frame = tk.Frame(self, relief="ridge", bg="gray")
        self.dilution_volume_frame.grid(column=2, row=16, pady=5, sticky=tk.NW)
        self.dilution_volume_selection = custom_widgets.Volume_selection(
            parent=self.dilution_volume_frame, title="Dilution solvent volume (mL)", options=options)

        # Display information
        self.display_frame = tk.LabelFrame(
            self, text="Progress and information ")
        self.display_frame.grid(column=0, rowspan=6, columnspan=4,
                                row=50, padx=15, pady=10)
        self.information = custom_widgets.Information_display(
            self.display_frame, width=150, height=12)

        # Run and stop buttons
        self.run_button = Button(
            self, text="Start sampling", style="Green.TButton", command=lambda: self.run())
        self.run_button.grid(column=0, row=60, padx=10, pady=10)
        self.stop_button = Button(
            self, text="Pause / Stop", style="Red.TButton", command=lambda: self.stop())
        self.stop_button.grid(column=1, row=60, padx=10, pady=10)

    def monitor_reaction(self, simulation=False):
        chem_robot.set_stop_flag(stop=False)

        if not chem_robot.ready:
            simulation = True
            self.information.display_msg(
                "System not ready, run in the simulation mode:\n")
            time.sleep(0.5)
        else:
            self.information.display_msg("Start sampling...\n")

        reactor_plate = chem_robot.deck.get_current_reactor_slot()

        trash_plate = chem_robot.deck.get_plate_assignment("Trash")
        trash = (trash_plate, 'A1')

        GC_LC_plate = chem_robot.deck.get_plate_assignment("GC LC")

        GC_LC_start_number = self.GC_LC_selection.get_current()
        GC_LC_no_start = self.GC_LC_selection.get_current(format="A1")

        number_of_reaction = int(self.number_reaction.get())

        solvent_name = self.solvent_selection.get()
        solvent_info = chem_synthesis.locate_reagent(solvent_name)
        if "not found" in solvent_info:
            messagebox.showinfo(" ", solvent_info)
            return
        else:
            solvent_plate_name = solvent_info["plate"]
            solvent_pos = solvent_info["vial"]
        solvent_slot = chem_robot.deck.get_slot_from_plate_name(
            solvent_plate_name)
        solvent_vial = (solvent_slot, solvent_pos)

        # sampling each reactor to GC-LC vials
        tip_type = "tips_50uL"
        tip_plate = chem_robot.deck.get_plate_assignment("Tips 50uL")
        self.tip_selection.set_current_tip_type(tip_type)
        for i in range(number_of_reaction):
            reactor_no = self.reactor_selection.get_current(format="A1")
            reactor_vial = (reactor_plate, reactor_no)

            GC_LC_no = self.GC_LC_selection.get_current(format="A1")
            GC_LC_vial = (GC_LC_plate, GC_LC_no)

            tip_no = self.tip_selection.get_current(format="A1")
            tip = (tip_plate, tip_no)

            sample_volume = self.sampling_volume_selection.get_value()/1000  # uL convert to mL
            dilution_volume = self.dilution_volume_selection.get_value()  # in mL already

            # " using tip {tip[1]}"
            message = f"Run {i+1} of {number_of_reaction}, sampling {sample_volume} mL from reactor {reactor_vial[1]} to GC/LC vial at {GC_LC_vial[1]}"
            self.information.display_msg(message, start_over=False)

            if simulation:
                time.sleep(1)  # run in the simulation mode
            else:
                if chem_robot.check_stop_status() == "stop":
                    return
                if self.reactor_decap.get():
                    chem_robot.decap(reactor_vial)
                if chem_robot.check_stop_status() == "stop":
                    return
                chem_robot.transfer_liquid(vial_from=reactor_vial, vial_to=GC_LC_vial,
                                           tip=tip, tip_type=tip_type,  trash=trash, volume=sample_volume, z=-40)
                if chem_robot.check_stop_status() == "stop":
                    return
                if self.reactor_decap.get():
                    chem_robot.recap(reactor_vial)
                if chem_robot.check_stop_status() == "stop":
                    return
            self.GC_LC_selection.next()
            self.reactor_selection.next()
            if not simulation:
                self.tip_selection.next()
            self.run_button["state"] = "enabled"

        # Add dilution solvent for each GC-LC vials
        tip_type = "tips_1000uL"
        self.tip_selection.set_current_tip_type(tip_type)
        tip_plate = chem_robot.deck.get_plate_assignment("Tips 1000uL")
        tip_no = self.tip_selection.get_current(format="A1")
        tip = (tip_plate, tip_no)
        if not simulation:
            chem_robot.pickup_tip(tip)
        if chem_robot.check_stop_status() == "stop":
            return
        if not simulation:
            chem_robot.decap(solvent_vial)
        if chem_robot.check_stop_status() == "stop":
            return
        GC_LC_no = GC_LC_no_start
        self.GC_LC_selection.set_current(GC_LC_start_number)
        self.GC_LC_selection.highlight_current()

        self.information.display_msg(
            "Sampling competed, starting to add dilution solvent...", start_over=False)
        for i in range(number_of_reaction):
            GC_LC_no = self.GC_LC_selection.get_current(format="A1")
            GC_LC_vial = (GC_LC_plate, GC_LC_no)
            # " using tip {tip[1]}"
            message = f"Run {i+1} of {number_of_reaction}, adding dilution solvent {solvent_name} {dilution_volume} mL to GC/LC vial at {GC_LC_vial[1]}"
            self.information.display_msg(message, start_over=False)
            if not simulation:
                chem_robot.transfer_liquid(vial_from=solvent_vial, vial_to=GC_LC_vial,
                                           tip=None, trash=trash, volume=dilution_volume)
            else:
                time.sleep(1)
            self.GC_LC_selection.next()

        if not simulation:
            chem_robot.drop_tip(trash)
        if not simulation:
            chem_robot.recap(solvent_vial)
        if not simulation:
            self.tip_selection.next()
            chem_robot.go_home()
        self.information.display_msg(
            "*Finished*\n", start_over=False)

    def run(self):
        self.run_button["state"] = "disabled"
        t = threading.Thread(target=self.monitor_reaction)
        t.start()

    def stop(self):
        chem_robot.set_stop_flag(stop=True)
        self.information.display_msg("Stopping......\n", start_over=False)
        self.run_button["state"] = "enabled"
        self.update()

    def reactor_update(self):
        current_reactor = chem_robot.deck.get_current_reactor()
        if current_reactor != self.current_reactor:
            self.reactor_selection_frame.destroy()
            self.reactor_selection_frame = tk.Frame(
                self, width=300, height=260)
            self.reactor_selection_frame.grid(column=0, row=11, rowspan=2)
            self.reactor_selection = custom_widgets.Plate_on_screen(
                parent=self.reactor_selection_frame, plate_type=current_reactor,  current=0)
            self.current_reactor = current_reactor


class Workup_tab(ttk.Frame):
    def __init__(self, parent, tip_selection=None):
        ttk.Frame.__init__(self, parent)
        self.tip_selection = tip_selection

        # Title
        Label(self, text="Reaction Workup", style="Title.Label").grid(
            column=0, columnspan=4, row=0, pady=20)

        # Organic phase volume selector
        options = [{"text": "1.0 mL", "value": 1.0},
                   {"text": "2.0 mL", "value": 2.0},
                   {"text": "3.0 mL", "value": 3.0}
                   ]
        self.organic_volume_frame = tk.Frame(self, relief="ridge", bg="gray")
        self.organic_volume_frame.grid(
            column=1, row=13, padx=50, pady=5, sticky=tk.NW)
        self.organic_volume_selection = custom_widgets.Volume_selection(
            parent=self.organic_volume_frame, title="Organic (Top) layer (mL) ", options=options)

        # Aqueous phase volume selector
        options = [{"text": "0   mL", "value": 0.0},
                   {"text": "1.0 mL", "value": 1.0},
                   {"text": "2.0 mL", "value": 2.0}
                   ]
        self.aqueous_volume_frame = tk.Frame(self, relief="ridge", bg="gray")
        self.aqueous_volume_frame.grid(
            column=1, row=14, padx=50, pady=5, rowspan=2, sticky=tk.NW)
        self.aqueous_volume_selection = custom_widgets.Volume_selection(
            parent=self.aqueous_volume_frame, title="Aqueous (Bottom) layer (mL)", options=options)

        # Reactor selection
        self.reactor_selection_frame = tk.Frame(
            self, width=300, height=260)
        self.reactor_selection_frame.grid(column=0, row=11, rowspan=3)
        self.current_reactor = chem_robot.deck.get_current_reactor()
        self.reactor_selection = custom_widgets.Plate_on_screen(
            parent=self.reactor_selection_frame, plate_type=self.current_reactor,  current=0)

        # Decap option, reactor_decap.get() = True or False
        self.reactor_decap = tk.IntVar()
        ttk.Checkbutton(self, text="Remove cap of reactor before workup",
                        variable=self.reactor_decap).grid(column=0, row=14, padx=50, sticky=tk.SW)

        # Number of reactions selector
        self.number_frame = tk.LabelFrame(
            self, text="Number of reactions", fg="RoyalBlue4", font="Helvetica 11 bold")
        self.number_frame.grid(column=0, row=15, padx=50, sticky=tk.NW)
        self.number_reaction = ttk.Combobox(
            self.number_frame, state="readonly", font=('Helvetica', '11'))
        self.number_reaction["values"] = tuple(range(1, 21))
        self.number_reaction.current(0)
        self.number_reaction.grid(pady=5)

        # Workup cartridge/vial selector
        self.GC_LC_selection = tk.Frame(
            self, width=300, height=260)
        self.GC_LC_selection.grid(column=3, row=11, rowspan=3)
        self.GC_LC_selection = custom_widgets.Plate_on_screen(
            parent=self.GC_LC_selection, title="Workup plate", plate_type="reactor_square_8mL_20p")

        # show the picture of transfer
        canvas = Canvas(self, width=168, height=140)
        canvas.grid(column=2, row=11, rowspan=3, pady=10, sticky=tk.W)
        self.img = PhotoImage(file="./images/workup_direction.png")
        canvas.create_image(1, 1, anchor=tk.NW, image=self.img)

        # Display of information
        self.display_frame = tk.LabelFrame(
            self, relief="ridge", text="Progress and information")
        self.display_frame.grid(column=0, rowspan=6, columnspan=4,
                                row=50, padx=15, pady=10)
        self.information = custom_widgets.Information_display(
            self.display_frame, width=150, height=14)

        # Run, pause and stop buttons
        self.run_button = Button(
            self, text="Start ", style="Green.TButton", command=lambda: self.run())
        self.run_button.grid(column=0, row=60, padx=10, pady=10)

        self.stop_button = Button(
            self, text="Pause / Stop", style="Red.TButton", command=lambda: self.stop())
        self.stop_button.grid(column=1, row=60, padx=10, pady=10)

    def workup_reaction(self, simulation=False):
        '''main entry for workup'''
        missing = chem_robot.deck.check_missing_assignment(required_plates=["Reagent", "Reactor", "Workup",
                                                                            "Tips 1000uL", "Trash", "Reaction caps"])
        if missing != "complete":
            retry = messagebox.askyesno(
                "Warning", f"Warning: No {missing} plate is assigned, continue?.")
            if not retry:
                return

        chem_robot.set_stop_flag(stop=False)
        if not chem_robot.ready:
            simulation = True
            self.information.display_msg(
                "System not ready, run in the simulation mode:\n")
            time.sleep(0.5)
        else:
            self.information.display_msg("Start work-up...\n")

        self.tip_selection.set_current_tip_type(tip_type="tips_1000uL")
        tip_no = self.tip_selection.get_current(format="A1")
        tip_plate = chem_robot.deck.get_plate_assignment("Tips 1000uL")

        reactor_no = self.reactor_selection.get_current(format="A1")
        reactor_plate = chem_robot.deck.get_current_reactor_slot()

        trash_plate = chem_robot.deck.get_plate_assignment("Trash")
        trash = (trash_plate, 'A1')

        workup_cartridge_plate = chem_robot.deck.get_plate_assignment("Workup")
        workup_cartridge_no = self.GC_LC_selection.get_current(format="A1")

        number_of_reaction = int(self.number_reaction.get())

        available_tip = len(chem_robot.deck.get_vial_list_by_plate_type(
            "tiprack_1000uL"))-self.tip_selection.get_current()

        available_reactor = len(chem_robot.deck.get_vial_list_by_plate_type(
            self.current_reactor))-self.reactor_selection.get_current()
        # available_workup_cartridge = len(chem_robot.deck.get_vial_list_by_plate_type(
        #     self.workup_plate_type))-self.GC_LC_selection.get_current()

        if available_tip < number_of_reaction:
            messagebox.showinfo(
                " ", "Warning: No enough tips! \n You will be promoted to refill tips during operation!")
            self.run_button["state"] = "enabled"

        if available_reactor < number_of_reaction:
            messagebox.showinfo(" ", "Warning: No enough reactor!")
            self.run_button["state"] = "enabled"
            return

        # if available_workup_cartridge < number_of_reaction:
        #     messagebox.showinfo(" ", "Warning: No enough workup container!")
        #     self.run_button["state"] = "enabled"
        #     return

        if not simulation:
            chem_robot.pipette.initialization()

        organic_volume = self.organic_volume_selection.get_value()
        aqueous_volume = self.aqueous_volume_selection.get_value()

        mm_per_mL = 6.02  # 3.5 for 15 mL vial
        if self.current_reactor == "reactor_square_8mL_20p":
            safty_margin = 0.0
        else:
            safty_margin = 2.0
        # samller safty_margin will lead to deeper suction
        tip_extraction_adjustment = aqueous_volume * mm_per_mL + safty_margin

        for i in range(number_of_reaction):
            if chem_robot.check_stop_status() == "stop":
                return
            tip_no = self.tip_selection.get_current(format="A1")
            tip = (tip_plate, tip_no)

            reactor_no = self.reactor_selection.get_current(format="A1")
            reactor = (reactor_plate, reactor_no)

            workup_cartridge_no = self.GC_LC_selection.get_current(
                format="A1")
            workup_cartridge = (workup_cartridge_plate, workup_cartridge_no)

            message = f"Run {i+1} of {number_of_reaction}, transfer {organic_volume} mL reaction mixture from reactor@ {reactor[1]} to workup plate position@ {workup_cartridge_no} using tip@ {tip[1]}"
            self.information.display_msg(message, start_over=False)
            if not simulation:
                if chem_robot.check_stop_status() == "stop":
                    return
                if self.reactor_decap.get():
                    chem_robot.decap(reactor)
                if chem_robot.check_stop_status() == "stop":
                    return
                chem_robot.pickup_tip(tip)
                self.tip_selection.next()

                if chem_robot.check_stop_status() == "stop":
                    return
                if chem_robot.transfer_liquid(vial_from=reactor, vial_to=workup_cartridge,
                                              volume=organic_volume, is_extraction=True, tip_extraction_adjustment=tip_extraction_adjustment) == "stop":
                    return
                if chem_robot.check_stop_status() == "stop":
                    return
                chem_robot.drop_tip(vial=trash)
                if self.reactor_decap.get():
                    chem_robot.recap(reactor)
                if chem_robot.check_stop_status() == "stop":
                    return
            else:
                time.sleep(1)  # run in the simulation mode

            # Move to next item (tip, reactor...)
            self.reactor_selection.next()
            self.GC_LC_selection.next()
        self.information.display_msg(
            "Finished***********\n", start_over=False)
        self.run_button["state"] = "enabled"

    def run(self):
        self.run_button["state"] = "disabled"
        self.update()
        t = threading.Thread(target=self.workup_reaction)
        t.start()

    def stop(self):
        chem_robot.set_stop_flag(stop=True)
        self.information.display_msg("Stopping......\n", start_over=False)
        self.run_button["state"] = "enabled"

    def reactor_update(self):
        current_reactor = chem_robot.deck.get_current_reactor()
        if current_reactor != self.current_reactor:
            self.reactor_selection_frame.destroy()
            self.reactor_selection_frame = tk.Frame(
                self, width=300, height=260)
            self.reactor_selection_frame.grid(column=0, row=11, rowspan=3)
            self.reactor_selection = custom_widgets.Plate_on_screen(
                parent=self.reactor_selection_frame, plate_type=current_reactor,  current=0)
            self.current_reactor = current_reactor


# Plate Calibration, accessed from menu - calibration
class Plate_calibration(ttk.Frame):
    def __init__(self):
        self.popup_window = Toplevel()
        self.popup_window.title("Plate Calibration ")

        # Slot selector
        self.current_slot = 5
        self.slot_frame = tk.Frame(
            self.popup_window, relief="ridge", bg="gray")
        self.slot_frame.grid(column=1, row=0, padx=10, pady=10, rowspan=3)
        slot_list = chem_robot.deck.get_vial_list_by_plate_type(
            plate_type="deck")
        self.slot_selection = custom_widgets.Item_selection_on_screen(
            parent=self.slot_frame, slot_list=slot_list, COLS=5, ROWS=3, current=self.current_slot)
        ttk.Label(self.popup_window, text="Select C3 to calibrate the current reactor ", style="Default.Label").grid(
            column=1, row=4, padx=10, pady=10)
        move_botton = Button(self.popup_window, text="Move to selected slot @", style="Default.TButton",
                             command=lambda: self.move_to_plate())

        move_botton.grid(column=1, row=5, pady=5)

        Label(self.popup_window, text=" ").grid(
            column=1, row=7, padx=10, pady=10)
        # Move functions as an LabelFrame
        self.move_frame = tk.LabelFrame(
            self.popup_window, text="Move axies (X, Y, Z1, Z2, Z3)", fg="RoyalBlue4", font="Helvetica 11 bold")
        self.move_frame.grid(column=0, columnspan=4, row=10,
                             padx=20, pady=10, sticky=tk.W)
        self.move_axies = custom_widgets.Move_axes(
            parent=self.move_frame, robot=chem_robot)

        # Save buttons
        Label(self.popup_window, text=" ").grid(
            column=1, row=16, padx=10, pady=10)
        self.button_save = Button(self.popup_window, text="Save calibration", style="Red.TButton",
                                  command=lambda: self.save_calibration_plate())
        self.button_save.grid(column=1, row=20, padx=0, pady=10)
        # Exit buttons
        self.button_exit = Button(self.popup_window, text="Exit", style="Default.TButton",
                                  command=lambda: self.exit())
        self.button_exit.grid(column=2, row=20, padx=0, pady=10)
        self.button_save.focus_force()
        self.popup_window.grab_set()  # keep this pop window focused

    def save_calibration_plate(self):
        plate_for_calibration = self.slot_selection.get_current(format="A1")
        if plate_for_calibration == "C3":
            plate_for_calibration = chem_robot.deck.get_current_reactor_slot()
        print("plate_for_calibration: ", plate_for_calibration)
        x = chem_robot.get_axe_position("x")
        y = chem_robot.get_axe_position("y")
        current_head = self.move_axies.get_current_head()
        z = chem_robot.get_axe_position(current_head)
        coordinate_of_vial = chem_robot.deck.vial_coordinate(plate=plate_for_calibration,
                                                             vial='A1')
        calibration_data = [x-coordinate_of_vial['x']-chem_robot.deck.head_offsets[current_head][0],
                            y-coordinate_of_vial['y']-chem_robot.deck.head_offsets[current_head][1],
                            z-coordinate_of_vial['z']]
        chem_robot.deck.save_calibration(plate=plate_for_calibration,
                                         calibration_data=calibration_data)
        chem_robot.update()

    def exit(self):
        self.popup_window.destroy()

    def move_to_plate(self):
        slot = chem_robot.deck.get_vial_list_by_plate_type(
            plate_type="deck")[self.slot_selection.get_current()]
        vial_to = (slot, "A1")
        current_head = self.move_axies.get_current_head()
        chem_robot.move_to(head=current_head, vial=vial_to,
                           use_allow_list=False)


# Tip Calibration, accessed from menu - calibration
class Tip_calibration(ttk.Frame):
    def __init__(self):
        self.popup_window = Toplevel()
        self.popup_window.title("Tip Calibration ")

        # Slot selector
        move_botton = Button(self.popup_window, text="Move to tip rack @", style="Default.TButton",
                             command=lambda: self.move_to_tip_rack())
        move_botton.grid(column=1, row=0, padx=40, pady=5)
        # Label(self.popup_window, text=" ").grid(column=1, row=7, padx=10, pady=10)

        # Move functions as an LabelFrame
        self.move_frame = tk.LabelFrame(
            self.popup_window, text="Move axies (X, Y, Z1, Z2, Z3)", fg="RoyalBlue4", font="Helvetica 11 bold")
        self.move_frame.grid(column=0, columnspan=4, row=10,
                             padx=20, pady=10, sticky=tk.W)
        self.move_axies = custom_widgets.Move_axes(
            parent=self.move_frame, robot=chem_robot)

        # Save buttons
        Label(self.popup_window, text=" ").grid(
            column=1, row=16, padx=10, pady=10)
        self.button_save = Button(self.popup_window, text="Save calibration", style="Red.TButton",
                                  command=lambda: self.save_calibration_tip())
        self.button_save.grid(column=1, row=20, padx=0, pady=10)
        self.button_save.focus_force()
        self.popup_window.grab_set()  # keep this pop window focused

        # Cancel buttons
        self.button_exit = Button(self.popup_window, text="Exit ", style="Default.TButton",
                                  command=lambda: self.exit())
        self.button_exit.grid(column=2, row=20, padx=0, pady=10)

    def save_calibration_tip(self, tip="tips_1000uL"):
        ''' the Tips was considered as plate name for simiplicity '''
        z = chem_robot.get_axe_position(axe=LIQUID)
        # tip_plate_50 = chem_robot.deck.get_plate_assignment("Tips 50uL")
        # tip_plate_1000 = chem_robot.deck.get_plate_assignment("Tips 1000uL")
        chem_robot.deck.save_calibration(plate="tips_1000uL",
                                         calibration_data=[0, 0, z])
        chem_robot.update()

    def exit(self):
        self.popup_window.destroy()

    def move_to_tip_rack(self):
        tip_plate_1000 = chem_robot.deck.get_plate_assignment("Tips 1000uL")
        vial_to = (tip_plate_1000, "A1")
        chem_robot.move_to(head=LIQUID, vial=vial_to)


class Reference_calibration(ttk.Frame):
    def __init__(self):
        self.popup_window = Toplevel()
        self.popup_window.title("Reference Point Calibration")

        # Move functions as an LabelFrame
        self.move_frame = tk.LabelFrame(
            self.popup_window, text="Move axies (X, Y, Z1, Z2, Z3)", fg="RoyalBlue4", font="Helvetica 11 bold")
        self.move_frame.grid(column=0, columnspan=4, row=10,
                             padx=20, pady=10, sticky=tk.W)
        self.move_axies = custom_widgets.Move_axes(
            parent=self.move_frame, robot=chem_robot)
        # Save buttons
        self.button_save_z1 = Button(self.popup_window, text="Save calibration (Z1)", style="Red.TButton",
                                     command=lambda: self.save_calibration("Z1"))
        self.button_save_z1.grid(column=0, row=20, padx=0, pady=10)
        self.button_save_z2 = Button(self.popup_window, text="Save calibration (Z2)", style="Red.TButton",
                                     command=lambda: self.save_calibration("Z2"))
        self.button_save_z2.grid(column=1, row=20, padx=0, pady=10)
        Label(self.popup_window, text=" ").grid(
            column=1, row=16, padx=10, pady=10)
        self.button_save_z3 = Button(self.popup_window, text="Save calibration (Z3)", style="Red.TButton",
                                     command=lambda: self.save_calibration("Z3"))
        self.button_save_z3.grid(column=2, row=20, padx=0, pady=10)
        # Exit buttons
        self.button_exit = Button(self.popup_window, text="Exit", style="Default.TButton",
                                  command=lambda: self.exit())
        self.button_exit.grid(column=3, row=20, padx=0, pady=10)
        self.button_exit.focus_force()
        self.popup_window.grab_set()  # keep this pop window focused

    def save_calibration(self, head="Z1"):
        # the smoothieware has a strange problem on max speed, I have to work around by double (*2) the steps_per_mm
        ''' the head name Z1, Z2 or Z3 was considered as plate name for simiplicity '''
        # example: [0, 0, 132.1] is the coordinate (x, y, z) vs. the ref point
        # "Z1": [0, 0, 132.1],
        # "Z2": [0, 0, 129.6],
        # "Z3": [0, 0, 125.4],
        # "Tips": 106.5
        current_head = head
        calibration_data = chem_robot.deck.calibration[current_head]
        x = chem_robot.xy_platform.get_position('x')
        y = chem_robot.xy_platform.get_position('y')
        z = chem_robot.z_platform.get_position(head=current_head)
        calibration_data = [x, y, z]
        chem_robot.deck.save_calibration(plate=current_head,
                                         calibration_data=calibration_data)
        chem_robot.update()

    def exit(self):
        self.popup_window.destroy()


# Reagent distrubution - transfer one reagent (solvents) to multiple reacters
class Liquid_distrubution():
    def __init__(self, tip_selection=None, title="Quench reaction", liquids=[]):
        self.tip_selection = tip_selection
        self.popup_window = Toplevel()
        self.popup_window.title(title)

        # Solvent option
        self.solvent_frame = tk.Frame(self.popup_window)
        self.solvent_frame.grid(column=0, row=0, sticky=tk.N)
        self.liquid_selection = custom_widgets.Multiple_reagents(
            parent=self.solvent_frame, liquids=liquids, chem_synthesis=chem_synthesis)

        # Number of reactions selection
        Label(self.popup_window, text=" ").grid(row=5, sticky=tk.W)
        self.number_frame = tk.LabelFrame(
            self.popup_window, text="Number of reactions", fg="RoyalBlue4", font="Helvetica 11 bold")
        self.number_frame.grid(column=0, row=6, sticky=tk.E, padx=10, pady=10)
        self.number_reaction = ttk.Combobox(
            self.number_frame, state="readonly", font=('Helvetica', '11'))
        self.number_reaction["values"] = tuple(range(1, 21))
        self.number_reaction.current(0)  # set the selected item
        self.number_reaction.grid(pady=5)

        # Reactor selector
        self.reactor_selection_frame = tk.Frame(
            self.popup_window, width=300, height=260)
        self.reactor_selection_frame.grid(
            column=1, row=0, rowspan=9, sticky=tk.N)
        self.current_reactor = chem_robot.deck.get_current_reactor()
        self.reactor_selection = custom_widgets.Plate_on_screen(
            parent=self.reactor_selection_frame, plate_type=self.current_reactor,  current=0)

        # Display information
        self.display_frame = tk.Frame(self.popup_window)
        self.display_frame.grid(column=0, rowspan=6, columnspan=4,
                                row=20, padx=15, pady=10)
        self.information = custom_widgets.Information_display(
            self.display_frame, width=100, height=14)

        # Run, stop and exit buttons
        self.run_button = Button(
            self.popup_window, text="Start", style="Green.TButton", command=lambda: self.run_thread())
        self.run_button.grid(column=0, row=30, pady=10)
        self.stop_button = Button(
            self.popup_window, text="Pause / Stop", style="Red.TButton", command=lambda: self.stop())
        self.stop_button.grid(column=1, row=30, pady=10)
        self.exit_button = Button(self.popup_window, text="Exit", style="Default.TButton",
                                  command=lambda: self.exit())
        self.exit_button.grid(column=2, row=30, padx=0, pady=10)
        self.exit_button.focus_force()
        self.popup_window.grab_set()  # keep this pop window focused

    def setup(self):
        number_of_reaction = int(self.number_reaction.get())
        current_tip = self.tip_selection.get_current()
        available_tip = len(chem_robot.deck.get_vial_list_by_plate_type(
            "tiprack_1000uL"))-current_tip
        available_reactor = len(chem_robot.deck.get_vial_list_by_plate_type(
            self.current_reactor))-self.reactor_selection.get_current()
        if available_tip < number_of_reaction:
            self.information.display_msg(
                "Warning: No enough tip, please refill tips.", start_over=False)
            return
        if available_reactor < number_of_reaction:
            self.information.display_msg(
                "Warning: No enough reactor.",  start_over=False)
            return

        ok = messagebox.askokcancel(
            "Warning", f"Please make sure:\n 1) Reactor vials are uncapped.\n  2) All reagent vials are secured in the plate.")
        if not ok:
            return

        missing = chem_robot.deck.check_missing_assignment()
        if missing != "complete":
            retry = messagebox.askyesno(
                "Warning", f"Warning: No {missing} plate is assigned, continue?.")
            if not retry:
                return

        liquids = self.liquid_selection.get_reagents()
        # format of liquids = [{'name': 'NaCl-water', 'plate': 'plate_50mL:003', 'position': 'A3', 'type': 'solution', 'amount': 0.5}]

        if liquids == []:
            return
        if not chem_robot.ready:
            self.information.display_msg(
                "Robot not ready! Please connect and home robot.", start_over=False)
            return
        chem_robot.pipette.initialization()
        reactor_plate = chem_robot.deck.get_current_reactor_slot()
        reactor_start = self.reactor_selection.get_current(
            format="A1")  # non-numerical format e.g., A1
        reactor_start_number = self.reactor_selection.get_current()
        for liquid in liquids:
            volume = liquid["amount"]
            solvent_plate_name = liquid['plate']
            solvent_pos = liquid['position']
            solvent_name = liquid['name']
            is_volatile = liquid["is_volatile"]
            if volume > 0.05:
                tip_type = "tips_1000uL"
                tip_plate = chem_robot.deck.get_plate_assignment("Tips 1000uL")
                self.tip_selection.set_current_tip_type(tip_type)
                tip_no = self.tip_selection.get_current(format="A1")
                tip = (tip_plate, tip_no)
            elif volume <= 0.05:
                tip_type = "tips_50uL"
                tip_plate = chem_robot.deck.get_plate_assignment("Tips 50uL")
                self.tip_selection.set_current_tip_type(tip_type)
                tip_no = self.tip_selection.get_current(format="A1")
                tip = (tip_plate, tip_no)

            trash_plate = chem_robot.deck.get_plate_assignment("Trash")
            trash = (trash_plate, 'A1')

            solvent_slot = chem_robot.deck.get_slot_from_plate_name(
                solvent_plate_name)
            solvent_vial = (solvent_slot, solvent_pos)

            self.information.display_msg("Starting transfering...")
            # prepare
            self.run_button.focus_force()
            self.popup_window.grab_set()  # keep this pop window focused
            self.exit_button["state"] = "disabled"
            self.run_button["state"] = "disabled"

            # Use one tip for all transfers
            chem_robot.decap(solvent_vial)
            if chem_robot.check_stop_status() == "stop":
                return
            chem_robot.pickup_tip(tip, tip_type=tip_type)
            if chem_robot.check_stop_status() == "stop":
                return
            self.tip_selection.next()

            # adding solvent
            reactor_no = reactor_start
            self.reactor_selection.set_current(reactor_start_number)
            i = 0
            for i in range(number_of_reaction):
                reactor_no = self.reactor_selection.get_current(format="A1")
                reactor_vial = (reactor_plate, reactor_no)
                if chem_robot.stop_flag:
                    return ("stopped by user")
                message = f"Run {i+1} of {number_of_reaction}, adding solvent {solvent_name} {volume} mL to reactor at {reactor_vial[1]} using tip {tip[1]}"
                self.information.display_msg(message, start_over=False)
                chem_robot.transfer_liquid(vial_from=solvent_vial, vial_to=reactor_vial, tip_type=tip_type, is_volatile=is_volatile,
                                           tip=None, trash=trash, volume=volume)
                is_volatile = False
                if chem_robot.check_stop_status() == "stop":
                    return
                self.reactor_selection.next()
            if chem_robot.check_stop_status() == "stop":
                return
            chem_robot.recap(solvent_vial)
            if chem_robot.check_stop_status() == "stop":
                return
            chem_robot.drop_tip(vial=trash)

        self.information.display_msg(
            "*Finished*\n", start_over=False)

        chem_robot.go_home()
        self.popup_window.grab_release()
        self.exit_button["state"] = "normal"
        self.run_button["state"] = "normal"

    def run_thread(self):
        t = threading.Thread(target=self.setup)
        t.start()

    def exit(self):
        self.popup_window.destroy()

    def stop(self):
        chem_robot.set_stop_flag(stop=True)
        self.information.display_msg("Stopping......\n", start_over=False)
        self.run_button["state"] = "normal"


class Solid_distrubution():
    def __init__(self, title="Add solid", reagents=[]):
        self.popup_window = Toplevel()
        self.popup_window.title(title)

        # Solvent option
        self.solvent_frame = tk.Frame(self.popup_window)
        self.solvent_frame.grid(column=0, row=0, sticky=tk.N)
        self.liquid_selection = custom_widgets.Multiple_reagents(
            parent=self.solvent_frame, reagent_type="solid", liquids=reagents, chem_synthesis=chem_synthesis)

        # Number of reactions selection
        Label(self.popup_window, text=" ").grid(row=5, sticky=tk.W)
        self.number_frame = tk.LabelFrame(
            self.popup_window, text="Number of reactions", fg="RoyalBlue4", font="Helvetica 11 bold")
        self.number_frame.grid(column=0, row=6, sticky=tk.E, padx=10, pady=10)
        self.number_reaction = ttk.Combobox(
            self.number_frame, state="readonly", font=('Helvetica', '11'))
        self.number_reaction["values"] = tuple(range(1, 21))
        self.number_reaction.current(0)  # set the selected item
        self.number_reaction.grid(pady=5)

        # Reactor selector
        self.reactor_selection_frame = tk.Frame(
            self.popup_window, width=300, height=260)
        self.reactor_selection_frame.grid(
            column=1, row=0, rowspan=9, sticky=tk.N)
        self.current_reactor = chem_robot.deck.get_current_reactor()
        self.reactor_selection = custom_widgets.Plate_on_screen(
            parent=self.reactor_selection_frame, plate_type=self.current_reactor,  current=0)

        # Display information
        self.display_frame = tk.Frame(self.popup_window)
        self.display_frame.grid(column=0, rowspan=6, columnspan=4,
                                row=20, padx=15, pady=10)
        self.information = custom_widgets.Information_display(
            self.display_frame, width=100, height=14)

        # Run, stop and exit buttons
        self.run_button = Button(
            self.popup_window, text="Start", style="Green.TButton", command=lambda: self.run_thread())
        self.run_button.grid(column=0, row=30, pady=10)
        self.stop_button = Button(
            self.popup_window, text="Pause / Stop", style="Red.TButton", command=lambda: self.stop())
        self.stop_button.grid(column=1, row=30, pady=10)
        self.exit_button = Button(self.popup_window, text="Exit", style="Default.TButton",
                                  command=lambda: self.exit())
        self.exit_button.grid(column=2, row=30, padx=0, pady=10)
        self.exit_button.focus_force()
        self.popup_window.grab_set()  # keep this pop window focused

    def setup(self):
        number_of_reaction = int(self.number_reaction.get())
        available_reactor = len(chem_robot.deck.get_vial_list_by_plate_type(
            self.current_reactor))-self.reactor_selection.get_current()
        if available_reactor < number_of_reaction:
            self.information.display_msg(
                "Warning: No enough reactor.",  start_over=False)
            return

        ok = messagebox.askokcancel(
            "Warning", f"Please make sure:\n 1) Reactor vials are uncapped.\n  2) All reagent vials are secured in the plate.")
        if not ok:
            return

        missing = chem_robot.deck.check_missing_assignment()
        if missing != "complete":
            retry = messagebox.askyesno(
                "Warning", f"Warning: No {missing} plate is assigned, continue?.")
            if not retry:
                return

        reagents = self.liquid_selection.get_reagents()
        # format of liquids = [{'name': 'NaCl-water', 'plate': 'plate_50mL:003', 'position': 'A3', 'type': 'solution', 'amount': 0.5}]

        if reagents == []:
            return
        if not chem_robot.ready:
            self.information.display_msg(
                "Robot not ready! Please connect and home robot.", start_over=False)
            return
        chem_robot.pipette.initialization()
        reactor_plate = chem_robot.deck.get_current_reactor_slot()
        reactor_start = self.reactor_selection.get_current(
            format="A1")  # non-numerical format e.g., A1
        reactor_start_number = self.reactor_selection.get_current()
        for reagent in reagents:
            amount = reagent["amount"]
            solvent_plate_name = reagent['plate']
            solvent_pos = reagent['position']
            solvent_name = reagent['name']
            mmol_per_tablet = chem_synthesis.locate_reagent(solvent_name)[
                'amount']
            solvent_slot = chem_robot.deck.get_slot_from_plate_name(
                solvent_plate_name)
            solvent_vial = (solvent_slot, solvent_pos)

            self.information.display_msg("Starting transfering...")
            # prepare
            self.run_button.focus_force()
            self.popup_window.grab_set()  # keep this pop window focused
            self.exit_button["state"] = "disabled"
            self.run_button["state"] = "disabled"

            chem_robot.decap(solvent_vial)
            if chem_robot.check_stop_status() == "stop":
                return
            reactor_no = reactor_start
            self.reactor_selection.set_current(reactor_start_number)
            i = 0
            for i in range(number_of_reaction):
                reactor_no = self.reactor_selection.get_current(format="A1")
                reactor_vial = (reactor_plate, reactor_no)
                if chem_robot.stop_flag:
                    return ("stopped by user")
                message = f"Run {i+1} of {number_of_reaction}, adding solid {solvent_name} {amount} mmol to reactor at {reactor_vial[1]}"
                self.information.display_msg(message, start_over=False)
                number_of_tablet = int(math.ceil(amount/mmol_per_tablet))
                print("amount/mmol_per_tablet", amount, mmol_per_tablet,
                      amount/mmol_per_tablet, number_of_tablet)
                chem_robot.transfer_tablet(
                    vial_from=solvent_vial, vial_to=reactor_vial, number_of_tablet=number_of_tablet)
                if chem_robot.check_stop_status() == "stop":
                    return
                self.reactor_selection.next()
            if chem_robot.check_stop_status() == "stop":
                return
            chem_robot.recap(solvent_vial)
            if chem_robot.check_stop_status() == "stop":
                return

        self.information.display_msg(
            "*Finished*\n", start_over=False)

        chem_robot.go_home()
        self.popup_window.grab_release()
        self.exit_button["state"] = "normal"
        self.run_button["state"] = "normal"

    def run_thread(self):
        t = threading.Thread(target=self.setup)
        t.start()

    def exit(self):
        self.popup_window.destroy()

    def stop(self):
        chem_robot.set_stop_flag(stop=True)
        self.information.display_msg("Stopping......\n", start_over=False)
        self.run_button["state"] = "normal"


class Manual_control():
    def __init__(self, tip_selector=None):
        self.tip_selector = tip_selector
        self.popup_window = Toplevel()
        self.popup_window.title("Manual Controls ")

        self.menu = Menu(self.popup_window, bg="lightgrey", fg="black")

        self.home_menu = Menu(self.menu, tearoff=0)
        self.home_menu.add_command(label="Home all axes",
                                   command=lambda: chem_robot.home_all())
        self.home_menu.add_command(label="Home Z axes only",
                                   command=lambda: chem_robot.home_all_z())
        self.menu.add_cascade(label="Home-Robot ", menu=self.home_menu)

        self.return_menu = Menu(self.menu, tearoff=0)
        self.return_menu.add_command(label="Return to safe position",
                                     command=lambda: chem_robot.go_home())
        self.menu.add_cascade(label="Return ", menu=self.return_menu)

        self.pipette_menu = Menu(self.menu, tearoff=0)
        self.pipette_menu.add_command(
            label="Reset pipette", command=lambda: chem_robot.pipette.initialization())
        self.pipette_menu.add_command(
            label="Eject tip", command=lambda: chem_robot.pipette.send_drop_tip_cmd())
        self.menu.add_cascade(label="Pipette  ", menu=self.pipette_menu)

        self.gripper_menu = Menu(self.menu, tearoff=0)
        self.gripper_menu.add_command(
            label="Reset gripper", command=lambda: chem_robot.gripper.initialization())
        self.gripper_menu.add_command(
            label="Gripper open (100%)", command=lambda: chem_robot.gripper.gripper_open(100))
        self.gripper_menu.add_command(
            label="Gripper open (80%)", command=lambda: chem_robot.gripper.gripper_open(80))
        self.gripper_menu.add_command(
            label="Gripper open (50%)", command=lambda: chem_robot.gripper.gripper_open(50))
        self.gripper_menu.add_command(
            label="Gripper open (30%)", command=lambda: chem_robot.gripper.gripper_open(30))
        self.gripper_menu.add_command(
            label="Gripper close", command=lambda: chem_robot.gripper.gripper_open(0))
        self.gripper_menu.add_command(
            label="Gripper rotate 90 degree", command=lambda: chem_robot.gripper.rotate(90))
        self.menu.add_cascade(label="Gripper  ", menu=self.gripper_menu)

        tk.Tk.config(self.popup_window, menu=self.menu)

        # Slot selector
        self.current_slot = 8
        Label(self.popup_window, text="Select current slot",
              style="Default.Label").grid(column=0, row=4, pady=5)
        self.slot_frame = tk.Frame(
            self.popup_window, relief="ridge", bg="gray")
        self.slot_frame.grid(column=0, row=5)
        slot_list = chem_robot.deck.get_vial_list_by_plate_type(
            plate_type="deck")
        self.slot_selection = custom_widgets.Item_selection_on_screen(
            parent=self.slot_frame, slot_list=slot_list, COLS=5, ROWS=3, current=self.current_slot)

        # Vial selector
        self.current_vial = 0
        Label(self.popup_window, text="Select current vial",
              style="Default.Label").grid(column=1, row=4, pady=5)
        self.vial_frame = tk.Frame(self.popup_window)
        self.vial_frame.grid(column=1, row=5, sticky=tk.N)
        slot_list = chem_robot.deck.get_vial_list_by_plate_type(
            plate_type="plate_5mL")
        col_row = chem_robot.deck.get_cols_rows_by_plate_type(
            plate_type="plate_5mL")
        self.vial_selection = custom_widgets.Item_selection_popup(
            parent=self.vial_frame, title="Current Vial:  ", slot_list=slot_list, COLS=col_row["columns"], ROWS=col_row["rows"], current=self.current_vial)

        # Z1 functions
        self.labelframe_z1 = tk.LabelFrame(
            self.popup_window, text="Liquid", fg="RoyalBlue4", font="Helvetica 11 bold")
        self.labelframe_z1.grid(
            column=0, row=10, padx=20, pady=20, sticky=tk.N)
        Button(self.labelframe_z1, text="Move to selected position", style="Green.TButton",
               command=lambda: self.move_to_plate("Z1")).grid(row=0, padx=10, pady=10, columnspan=2, sticky=tk.W)
        Button(self.labelframe_z1, text="Pickup Tip", style="Default.TButton",
               command=lambda: self.test_pickup_tip()).grid(row=1, padx=10, pady=10, sticky=tk.W)
        Button(self.labelframe_z1, text="Aspirate", style="Default.TButton",
               command=lambda: self.test_aspirate()).grid(row=2, padx=10, pady=10, sticky=tk.W)
        Button(self.labelframe_z1, text="Dispense", style="Default.TButton",
               command=lambda: self.test_dispense()).grid(row=3, padx=10, pady=10, sticky=tk.W)
        Button(self.labelframe_z1, text="Eject Tip", style="Default.TButton",
               command=lambda: self.test_eject_tip()).grid(row=4, padx=10, pady=10, sticky=tk.W)
        # Reaction volume selector
        self.volume_frame = tk.Frame(
            self.labelframe_z1, relief="ridge", bg="gray")
        self.volume_frame.grid(column=1, row=2, pady=10, sticky=tk.N)
        self.volume_selection = custom_widgets.Volume_entry(
            parent=self.volume_frame, title="Volume (mL)")
        self.slot_frame.focus_force()
        self.popup_window.grab_set()  # keep this pop window focused

        # Z2 functions
        self.labelframe_z2 = tk.LabelFrame(
            self.popup_window, text="Tablet", fg="RoyalBlue4", font="Helvetica 11 bold")
        self.labelframe_z2.grid(column=1, row=10, pady=20, sticky=tk.N)
        Button(self.labelframe_z2, text="Move to selected position", style="Green.TButton",
               command=lambda: self.move_to_plate("Z2")).grid(row=0, padx=10, pady=15, columnspan=2,  sticky=tk.W)
        Button(self.labelframe_z2, text="Pickup Tablet", style="Default.TButton",
               command=lambda: self.test_pickup_tablet()).grid(row=1, padx=10, pady=15, sticky=tk.W)
        Button(self.labelframe_z2, text="Drop Tablet", style="Default.TButton",
               command=lambda: self.test_drop_tablet()).grid(row=2, padx=10, pady=15, sticky=tk.W)
        Button(self.labelframe_z2, text="Clean Needle", style="Default.TButton",
               command=lambda: self.test_clean_needle()).grid(row=3, padx=10, pady=15, sticky=tk.W)

        # Z3 functions
        self.labelframe_z3 = tk.LabelFrame(
            self.popup_window, text="Capper", fg="RoyalBlue4", font="Helvetica 11 bold")
        self.labelframe_z3.grid(
            column=2, row=10, padx=20, pady=20, sticky=tk.N)
        Button(self.labelframe_z3, text="Move to selected position", style="Green.TButton",
               command=lambda: self.move_to_plate("Z3")).grid(row=0, padx=10, pady=10, columnspan=2, sticky=tk.W)
        Button(self.labelframe_z3, text="  Decap ", style="Default.TButton",
               command=lambda: self.test_decap()).grid(row=1, padx=10, pady=10, sticky=tk.W)
        Button(self.labelframe_z3, text=" Recap", style="Default.TButton",
               command=lambda: self.test_recap()).grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
        Button(self.labelframe_z3, text=" Pickup Cap from", style="Default.TButton",
               command=lambda: self.test_pickup_cap()).grid(row=3, padx=10, pady=10, sticky=tk.W)

        # Cap selector
        self.cap_frame = tk.Frame(
            self.labelframe_z3, relief="ridge", bg="gray")
        self.cap_frame.grid(column=0, row=8, rowspan=2, columnspan=2)
        slot_list = [
            "A1",
            "B1",
            "C1",
            "D1",
            "A2",
            "B2",
            "C2",
            "D2",
            "A3",
            "B3",
            "C3",
            "D3",
            "A4",
            "B4",
            "C4",
            "D4",
            "A5",
            "B5",
            "C5",
            "D5"
        ]
        col_row = chem_robot.deck.get_cols_rows_by_plate_type(
            plate_type="caps")
        self.cap_selection = custom_widgets.Item_selection_on_screen(
            parent=self.cap_frame, slot_list=slot_list, COLS=col_row["columns"], ROWS=col_row["rows"], current=0)
        Button(self.labelframe_z3, text="Return Cap to", style="Default.TButton",
               command=lambda: self.test_return_cap()).grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)

        # Move functions as an LabelFrame
        self.move_frame = tk.LabelFrame(
            self.popup_window, text="Move axies (X, Y, Z1, Z2, Z3)", fg="RoyalBlue4", font="Helvetica 11 bold")
        self.move_frame.grid(column=0, columnspan=4, row=15,
                             padx=20, sticky=tk.W)
        self.move_axies = custom_widgets.Move_axes(
            parent=self.move_frame, robot=chem_robot)

    def move_to_plate(self, head):
        slot = self.slot_selection.get_current(format="A1")
        vial = self.vial_selection.get_current(format="A1")
        vial_to = (slot, vial)
        chem_robot.move_to(head=head, vial=vial_to, use_allow_list=False)

    def test_decap(self):
        slot = self.slot_selection.get_current(format="A1")
        vial = self.vial_selection.get_current(format="A1")
        vial_to = (slot, vial)
        chem_robot.move_to(head=CAPPER, vial=vial_to)
        chem_robot.decap(vial=vial_to)

    def test_recap(self):
        slot = self.slot_selection.get_current(format="A1")
        vial = self.vial_selection.get_current(format="A1")
        vial_to = (slot, vial)
        chem_robot.move_to(head=CAPPER, vial=vial_to)
        chem_robot.recap(vial=vial_to)

    def test_pickup_cap(self):
        cap_no = self.cap_selection.get_current(format="A1")
        cap_plate = chem_robot.deck.get_plate_assignment("Reaction caps")
        chem_robot.pickup_cap((cap_plate, cap_no))

    def test_return_cap(self):
        cap_no = self.cap_selection.get_current(format="A1")
        cap_plate = chem_robot.deck.get_plate_assignment("Reaction caps")
        chem_robot.return_cap((cap_plate, cap_no))

    def test_pickup_tablet(self):
        slot = self.slot_selection.get_current(format="A1")
        vial = self.vial_selection.get_current(format="A1")
        vial_to = (slot, vial)
        chem_robot.pickup_tablet(vial=vial_to)

    def test_drop_tablet(self):
        slot = self.slot_selection.get_current(format="A1")
        vial = self.vial_selection.get_current(format="A1")
        vial_to = (slot, vial)
        chem_robot.drop_tablet(vial=vial_to)

    def test_clean_needle(self):
        # slot = self.slot_selection.get_current(format="A1")
        # vial = self.vial_selection.get_current(format="A1")
        vial_to = ("C1", "D4")
        chem_robot.clean_up_needle(vial=vial_to)

    def test_pickup_tip(self):
        tip_no = self.tip_selector.get_current(format="A1")
        tip_plate = chem_robot.deck.get_plate_assignment("Tips 1000uL")
        chem_robot.pickup_tip((tip_plate, tip_no))

    def test_aspirate(self):
        volume = self.volume_selection.get()
        if volume == False:
            messagebox.showinfo(
                " ", "Please input a valid volume in mL.")
        slot = self.slot_selection.get_current(format="A1")
        vial = self.vial_selection.get_current(format="A1")
        vial_to = (slot, vial)
        chem_robot.aspirate(vial=vial_to, volume=int(volume*1000))
        chem_robot.back_to_safe_position(head=LIQUID)
        chem_robot.pipette.set_transport_air_volume(volume=15)

    def test_dispense(self):
        slot = self.slot_selection.get_current(format="A1")
        vial = self.vial_selection.get_current(format="A1")
        vial_to = (slot, vial)
        chem_robot.dispense(vial=vial_to)
        chem_robot.back_to_safe_position(head=LIQUID)

    def test_eject_tip(self):
        chem_robot.pipette.send_drop_tip_cmd()


# Used in reagent distrubution
class Cap_operation():
    def __init__(self, option=""):
        self.popup_window = Toplevel()
        self.option = option
        self.popup_window.title(self.option)

        if self.option == "Cap reactors":
            reactor_column = 2
            cap_column = 0
            image_file = "./images/recap.png"
        else:
            reactor_column = 0
            cap_column = 2
            image_file = "./images/decap.png"

        # Reactor selector
        self.reactor_selection_frame = tk.Frame(
            self.popup_window, width=300, height=260)
        self.reactor_selection_frame.grid(
            column=reactor_column, row=7, padx=20, rowspan=9, sticky=tk.W)
        self.current_reactor = chem_robot.deck.get_current_reactor()
        self.reactor_selection = custom_widgets.Plate_on_screen(
            parent=self.reactor_selection_frame, plate_type=self.current_reactor,  current=0)

        # cap selection
        self.cap_selection = tk.Frame(
            self.popup_window, width=300, height=260)
        self.cap_selection.grid(column=cap_column, row=8,
                                padx=10, sticky=tk.N, rowspan=3)
        self.cap_selection = custom_widgets.Plate_on_screen(
            parent=self.cap_selection, title="Cap plate", plate_type="reactor_square_8mL_20p")

        # show picture of cap
        canvas = Canvas(self.popup_window, width=330, height=150)
        canvas.grid(column=1, row=8, pady=10, padx=50, rowspan=3)
        self.img = PhotoImage(file=image_file)
        canvas.create_image(1, 1, anchor=tk.NW, image=self.img)

        self.number_frame = tk.LabelFrame(
            self.popup_window, text="Number of reactors", fg="RoyalBlue4", font="Helvetica 11")
        self.number_frame.grid(
            column=0, row=19, columnspan=1, sticky=tk.W, padx=15)
        self.number_reaction = ttk.Combobox(
            self.number_frame, state="readonly", font=('Helvetica', '11'))
        self.number_reaction["values"] = tuple(range(1, 21))
        self.number_reaction.current(0)  # set the selected item
        self.number_reaction.grid(pady=5)

        # Display information
        self.display_frame = tk.LabelFrame(
            self.popup_window, text="Progress of operation")
        self.display_frame.grid(column=0, rowspan=6, columnspan=3,
                                row=20, sticky=tk.W, padx=15, pady=10)
        self.information = custom_widgets.Information_display(
            self.display_frame, width=130, height=14)

        # Run, stop and exit buttons
        self.run_button = Button(
            self.popup_window, text=self.option, style="Green.TButton", command=lambda: self.run_thread())
        self.run_button.grid(column=0, row=30, pady=10)
        self.stop_button = Button(
            self.popup_window, text="Pause / Stop ", style="Red.TButton", command=lambda: self.stop())
        self.stop_button.grid(column=1, row=30, pady=10)
        self.exit_button = Button(self.popup_window, text="Exit", style="Default.TButton",
                                  command=lambda: self.exit())
        self.exit_button.grid(column=2, row=30, padx=0, pady=10)
        self.exit_button.focus_force()
        self.popup_window.grab_set()  # keep this pop window focused

    def setup(self):
        chem_robot.set_stop_flag(stop=False)
        number_of_reaction = int(self.number_reaction.get())

        available_reactor = len(chem_robot.deck.get_vial_list_by_plate_type(
            self.current_reactor))-self.reactor_selection.get_current()

        if available_reactor < number_of_reaction:
            self.information.display_msg(
                "Warning: No enough reactor.",  start_over=False)
            return

        available_cap = len(chem_robot.deck.get_vial_list_by_plate_type(
            "caps"))-self.cap_selection.get_current()

        if available_cap < number_of_reaction:
            self.information.display_msg(
                "Warning: No enough cap.",  start_over=False)
            return

        if self.option == "Cap reactors":
            ok = messagebox.askokcancel(
                "Warning", f"Are reactors uncapped?")
            if not ok:
                return
            ok = messagebox.askokcancel(
                "Warning", f"Are there nough caps on cap plate?")
            if not ok:
                return
        else:
            ok = messagebox.askokcancel(
                "Warning", f"Are reactors capped?")
            if not ok:
                return
            ok = messagebox.askokcancel(
                "Warning", f"Are there empty spaces on cap plate?")
            if not ok:
                return

        missing = chem_robot.deck.check_missing_assignment()
        if missing != "complete":
            retry = messagebox.askyesno(
                "Warning", f"Warning: No {missing} plate is assigned, continue?.")
            if not retry:
                return

        if not chem_robot.ready:
            self.information.display_msg(
                "Robot not ready! Please connect and home robot.", start_over=False)
            return

        self.run_button.focus_force()
        self.popup_window.grab_set()  # keep this pop window focused
        self.exit_button["state"] = "disabled"
        self.run_button["state"] = "disabled"

        # cap operations, if option = cap or decap
        reactor_plate = chem_robot.deck.get_current_reactor_slot()
        cap_plate = chem_robot.deck.get_plate_assignment("Reaction caps")
        for i in range(number_of_reaction):
            reactor_no = self.reactor_selection.get_current(format="A1")
            reactor = (reactor_plate, reactor_no)
            cap_no = self.cap_selection.get_current(format="A1")
            cap = (cap_plate, cap_no)
            message = f"Run {i+1} of {number_of_reaction}, transfer cap for reactor@ {reactor[1]}"
            self.information.display_msg(message, start_over=False)
            if self.option == "Cap reactors":
                chem_robot.pickup_cap(cap)
                if chem_robot.check_stop_status() == "stop":
                    return
                chem_robot.recap(reactor)
                if chem_robot.check_stop_status() == "stop":
                    return
            else:
                chem_robot.decap(reactor)
                if chem_robot.check_stop_status() == "stop":
                    return
                chem_robot.return_cap(cap)
            self.reactor_selection.next()
            self.cap_selection.next()

        self.information.display_msg(
            "Finished**************\n", start_over=False)

        self.popup_window.grab_release()
        self.exit_button["state"] = "normal"
        self.run_button["state"] = "normal"
        chem_robot.go_home()

    def run_thread(self):
        t = threading.Thread(target=self.setup)
        t.start()

    def exit(self):
        self.popup_window.destroy()

    def stop(self):
        chem_robot.set_stop_flag(stop=True)
        self.information.display_msg("Stopping......\n", start_over=False)
        self.run_button["state"] = "normal"
        self.exit_button["state"] = "normal"


# This is the main entry of program
if __name__ == "__main__":
    now = datetime.now()
    time_stamp = now.strftime("%m-%d-%Y")
    logbook_folder = os.getcwd() + "/logs/"
    logbook_filename = logbook_folder + "Logbook-"+time_stamp+".log"
    logging.basicConfig(filename=logbook_filename,
                        format='%(asctime)s %(message)s', level=logging.INFO)
    # Start robot class
    chem_robot = robot.Robot()
    chem_synthesis = synthesis.Synthesis(
        reagent_file=Path("user_files/reagent_index.xlsx"))

    # Start GUI
    app = Main()

    # define styles
    style = ttk.Style()
    style.configure('lefttab.TNotebook', tabposition='wn')
    style.configure('Title.Label',
                    foreground="light green",
                    background="dark green",
                    font=('Helvetica', 18, 'bold italic'),
                    justify=tk.CENTER,
                    relief=tk.RIDGE
                    )

    style.configure('Default.Label',
                    foreground="black",
                    # background="dark green",
                    font=('Helvetica', 11, 'italic'),
                    justify=tk.CENTER,
                    relief=tk.RIDGE
                    )

    style.configure('Blue.Label',
                    foreground="blue4",
                    # background="dark green",
                    font=('Helvetica', 11),
                    justify=tk.CENTER,
                    relief=tk.RIDGE
                    )

    style.configure("Default.TButton",
                    foreground="Black",
                    font=('Helvetica', 11, 'italic'),
                    background="LightGrey")

    style.configure("Green.TButton",
                    foreground="blue",
                    background="green",
                    font=('Helvetica', 11, 'italic'))

    style.configure("Red.TButton",
                    foreground="red",
                    font=('Helvetica', 11, 'italic'),
                    background="red")

    style.configure("Plate.TButton",
                    foreground="black",
                    font=('Helvetica', 11, 'italic'),
                    width=18,
                    justify=tk.LEFT,
                    background="deepskyblue")

    style.configure("Plate_r.TButton",
                    foreground="blue",
                    font=('Helvetica', 11, 'italic'),
                    width=18,
                    justify=tk.LEFT,
                    background="deepskyblue")

    app.geometry("+0+0")  # set to window to the up/left conner of screen
    # app.state('zoomed')  # full screen mode

    app.mainloop()

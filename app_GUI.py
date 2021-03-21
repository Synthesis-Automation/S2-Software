# coding:utf-8
import json
import time
import socket
import threading
import logging
import random
from pathlib import Path

import tkinter as tk
from tkinter import ttk
from tkinter import Menu, Canvas, PhotoImage, Toplevel, filedialog, scrolledtext, messagebox, simpledialog
from tkinter.ttk import Notebook, Separator, Label, Button

from combinewave.robot import robot
from combinewave.chemical_synthesis import synthesis
from combinewave.tools import custom_widgets, helper
# CAPPER = 'Z1'...
from combinewave.parameters import CAPPER, LIQUID, TABLET, VERSION, SYSTEM_NAME, NEW_PLAN_HEADER


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
        self.file_menu.add_command(label="New synthesis plan",
                                   command=lambda: self.synthesis_tab.new_plan())
        self.file_menu.add_command(label="Open synthesis plan",
                                   command=lambda: self.synthesis_tab.open_plan())
        self.file_menu.add_command(label="Save synthesis plan",
                                   command=lambda: self.synthesis_tab.save_plan())
        self.file_menu.add_command(label="Save synthesis plan as new file",
                                   command=lambda: self.synthesis_tab.save_as_plan())
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Open synthesis plan as excel file",
                                   command=lambda: self.synthesis_tab.open_plan_excel(),
                                   accelerator="Ctrl+L")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.exit_gui)
        self.menu.add_cascade(label="File ", menu=self.file_menu)

        self.connect_menu = Menu(self.menu, tearoff=0)
        self.connect_menu.add_command(
            label="Copy", command=lambda: chem_robot.connect())
        self.menu.add_cascade(label="Edit ", menu=self.connect_menu)

        self.home_menu = Menu(self.menu, tearoff=0)
        self.home_menu.add_command(label="Home all",
                                   command=lambda: chem_robot.home_all())
        self.home_menu.add_command(label="Home Z only",
                                   command=lambda: chem_robot.home_all_z())
        # self.home_menu.add_command(label="Home X",
        #                            command=lambda: chem_robot.xy_platform.home_x())
        # self.home_menu.add_command(label="Home Y",
        #                            command=lambda: chem_robot.xy_platform.home_y())
        self.menu.add_cascade(label="Home-robot ", menu=self.home_menu)

        self.reset_menu = Menu(self.menu, tearoff=0)
        self.reset_menu.add_command(
            label="Reset pipette", command=lambda: chem_robot.pipette.initialization())
        self.reset_menu.add_command(
            label="Reset gripper", command=lambda: chem_robot.gripper.initialization())
        self.menu.add_cascade(label="Reset  ", menu=self.reset_menu)

        self.calibration_menu = Menu(self.menu, tearoff=0)
        self.calibration_menu.add_command(
            label="Plate Calibration", command=lambda: self.plate_calibration())
        self.calibration_menu.add_command(
            label="Tip Pickup Calibration", command=lambda: self.tip_calibration())
        self.calibration_menu.add_command(
            label="Deck Calibration", command=lambda: self.tip_calibration())
        self.menu.add_cascade(label="Calibration ", menu=self.calibration_menu)

        self.tools_menu = Menu(self.menu, tearoff=0)
        self.tools_menu.add_command(
            label="Solvent distribution", command=lambda: self.reagent_distrubution())
        self.tools_menu.add_command(
            label="Solid distribution", command=lambda: chem_robot.gripper.initialization())
        self.menu.add_cascade(label="Tools  ", menu=self.tools_menu)

        helpmenu = Menu(self.menu, tearoff=0)
        helpmenu.add_command(label="About", command=lambda: self.about())
        self.menu.add_cascade(label="Help", menu=helpmenu)
        tk.Tk.config(self, menu=self.menu)
        # End of main menu

        # Notebook tab
        self.notebook = Notebook(self, style='lefttab.TNotebook')

        connect_tab = Connect_tab(self.notebook)
        self.connect_img = PhotoImage(file=Path("./images/connect_t.png"))
        self.notebook.add(connect_tab, text="Connect\n",
                          image=self.connect_img, compound=tk.TOP)

        deck_tab = Deck_tab(self.notebook)
        self.deck_img = PhotoImage(file=Path("./images/deck_t.png"))
        self.notebook.add(deck_tab, text="Deck Setup\n",
                          image=self.deck_img, compound=tk.TOP)

        self.manual_control_tab = Manual_control_tab(self.notebook)
        self.manual_control_img = PhotoImage(
            file=Path("./images/manual_control_t.png"))
        self.notebook.add(
            self.manual_control_tab, text="Manual Control\n", image=self.manual_control_img, compound=tk.TOP)

        self.synthesis_tab = Synthesis_tab(self.notebook)
        self.synthesis_img = PhotoImage(file=Path("./images/synthesis_t.png"))
        self.notebook.add(self.synthesis_tab, text="Synthesis\n",
                          image=self.synthesis_img, compound=tk.TOP)

        self.monitor_tab = Monitor_tab(self.notebook)
        self.monitor_img = PhotoImage(file=Path("./images/monitor.png"))
        self.notebook.add(self.monitor_tab, text="Reaction Monitor\n",
                          image=self.monitor_img, compound=tk.TOP)

        self.workup_tab = Workup_tab(self.notebook)
        self.workup_img = PhotoImage(file=Path("./images/workup.png"))
        self.notebook.add(self.workup_tab, text="Reaction Workup\n",
                          image=self.workup_img, compound=tk.TOP)

        self.notebook.pack(fill=tk.BOTH, expand=1)
        self.notebook.bind("<ButtonRelease-1>", self.update_tip_by_tab_clicked)
        # End of Notebook tab setup

    def about(self):
        messagebox.showinfo(" ", SYSTEM_NAME + " " + VERSION)

    def update_tip_by_tab_clicked(self, event=None):
        # Make sure that all tip selection have the same current tip number
        time_list = [
            self.manual_control_tab.tip_selection.get_update_time(),
            self.synthesis_tab.tip_selection.get_update_time(),
            self.monitor_tab.tip_selection.get_update_time(),
            self.workup_tab.tip_selection.get_update_time(),
        ]
        index = time_list.index(max(time_list))
        if index == 0:
            current_tip = self.manual_control_tab.tip_selection.get_current()
        if index == 1:
            current_tip = self.synthesis_tab.tip_selection.get_current()
        if index == 2:
            current_tip = self.monitor_tab.tip_selection.get_current()
        if index == 3:
            current_tip = self.workup_tab.tip_selection.get_current()
        self.workup_tab.tip_selection.reset_current(current_tip)
        self.synthesis_tab.tip_selection.reset_current(current_tip)
        self.manual_control_tab.tip_selection.reset_current(current_tip)
        self.monitor_tab.tip_selection.reset_current(current_tip)
        chem_robot.deck.set_current_tip(current_tip)
        chem_robot.deck.save_current_tip()

    def reagent_distrubution(self):
        popup = Reagent_distrubution()
        self.wait_window(popup.t)

    def plate_calibration(self):
        popup = Plate_calibration()
        self.wait_window(popup.popup_window)

    def tip_calibration(self):
        popup = Tip_calibration()
        self.wait_window(popup.popup_window)

    def exit_gui(self):
        self.update_tip_by_tab_clicked()
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
        connect_btn = Button(self, text="Connect and home robot", style="Green.TButton",
                             command=lambda: self.connect())
        connect_btn.pack(pady=20)
        self.status = tk.Label(
            self, text="Robot Status: Not connected", fg="red", width=50)
        self.status.pack(side=tk.BOTTOM,  fill=tk.X)

    def connect(self):
        try:
            if not chem_robot.ready:
                if not chem_robot.is_connected:
                    chem_robot.connect()
                    chem_robot.home_all_z()
                    chem_robot.is_connected = True
                yes = messagebox.askyesno(
                    "Info", "Make sure no obstruction, home robot?")
                if not yes:
                    return False
                chem_robot.home_xy()
                chem_robot.pipette.initialization()
                chem_robot.gripper.initialization()
                chem_robot.ready = True
            self.status.configure(text="Robot Status: Ready",
                                  fg="green")
        except Exception:
            messagebox.showinfo(
                " ", "Connection failed, please check USB connection and try again.")


class Manual_control_tab(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)

        Label(self, text=" Manual Control ", style="Title.Label").grid(
            column=0, columnspan=4, row=0, padx=50, pady=10)

        # blank space
        tk.Label(self, text=" ".ljust(220),
                 bg="lightgrey").grid(column=0, columnspan=3, row=1, pady=5)
        # Slot selector
        self.current_slot = 5
        Label(self, text="Select current slot",
              style="Default.Label").grid(column=1, row=4, pady=5)
        self.slot_frame = tk.Frame(self, relief="ridge", bg="gray")
        self.slot_frame.grid(column=1, row=5)
        slot_list = chem_robot.deck.get_vial_list_by_plate_type(
            plate_type="deck")
        self.slot_selection = custom_widgets.Item_selection_on_screen(
            parent=self.slot_frame, slot_list=slot_list, COLS=5, ROWS=3, current=self.current_slot)

        # Vial selector
        self.current_vial = 0
        Label(self, text="Select current vial",
              style="Default.Label").grid(column=2, row=4, pady=5)
        self.vial_frame = tk.Frame(self)
        self.vial_frame.grid(column=2, row=5, sticky=tk.N)
        slot_list = chem_robot.deck.get_vial_list_by_plate_type(
            plate_type="plate_5mL")
        col_row = chem_robot.deck.get_cols_rows_by_plate_type(
            plate_type="plate_5mL")
        self.vial_selection = custom_widgets.Item_selection_popup(
            parent=self.vial_frame, title="Current Vial:  ", slot_list=slot_list, COLS=col_row["columns"], ROWS=col_row["rows"], current=self.current_vial)

        # blank space
        tk.Label(self, text=" ".ljust(220),
                 bg="lightgrey").grid(column=0, columnspan=3, row=6, pady=5)

        # Z1 functions
        self.labelframe_z1 = tk.LabelFrame(
            self, text="Capper", fg="RoyalBlue4", font="Helvetica 11 bold")
        self.labelframe_z1.grid(
            column=0, row=10, padx=20, pady=20, sticky=tk.N)
        Button(self.labelframe_z1, text="Move to selected position", style="Green.TButton",
               command=lambda: self.move_to_plate("Z1")).grid(row=0, padx=10, pady=15, sticky=tk.W)
        Button(self.labelframe_z1, text="  Decap ", style="Default.TButton",
               command=lambda: self.test_decap()).grid(row=1, padx=10, pady=15, sticky=tk.W)
        Button(self.labelframe_z1, text=" Recap", style="Default.TButton",
               command=lambda: self.test_recap()).grid(row=2, padx=10, pady=15, sticky=tk.W)
        Button(self.labelframe_z1, text=" Pickup Cap @", style="Default.TButton",
               command=lambda: self.test_pickup_cap()).grid(row=3, padx=10, pady=15, sticky=tk.W)
        # Cap selector
        self.cap_frame = tk.Frame(
            self.labelframe_z1, relief="ridge", bg="gray")
        self.cap_frame.grid(column=0, row=8)
        slot_list = chem_robot.deck.get_vial_list_by_plate_type(
            plate_type="caps")
        col_row = chem_robot.deck.get_cols_rows_by_plate_type(
            plate_type="caps")
        self.cap_selection = custom_widgets.Item_selection_on_screen(
            parent=self.cap_frame, slot_list=slot_list, COLS=col_row["columns"], ROWS=col_row["rows"], current=0)

        # Z2 functions
        self.labelframe_z2 = tk.LabelFrame(
            self, text="Tablet", fg="RoyalBlue4", font="Helvetica 11 bold")
        self.labelframe_z2.grid(column=1, row=10, pady=20, sticky=tk.N)
        Button(self.labelframe_z2, text="Move to selected position", style="Green.TButton",
               command=lambda: self.move_to_plate("Z2")).grid(row=0, padx=10, pady=15, sticky=tk.W)
        Button(self.labelframe_z2, text="Pickup Tablet", style="Default.TButton",
               command=lambda: self.test_pickup_tablet()).grid(row=1, padx=10, pady=15, sticky=tk.W)
        Button(self.labelframe_z2, text="Drop Tablet", style="Default.TButton",
               command=lambda: self.test_drop_tablet()).grid(row=2, padx=10, pady=15, sticky=tk.W)
        Button(self.labelframe_z2, text="Clean Needle", style="Default.TButton",
               command=lambda: self.test_clean_needle()).grid(row=3, padx=10, pady=15, sticky=tk.W)

        # Z3 functions
        self.labelframe_z3 = tk.LabelFrame(
            self, text="Liquid", fg="RoyalBlue4", font="Helvetica 11 bold")
        self.labelframe_z3.grid(column=2, row=10, pady=20, sticky=tk.N)
        Button(self.labelframe_z3, text="Move to selected position", style="Green.TButton",
               command=lambda: self.move_to_plate("Z3")).grid(row=0, padx=10, pady=15, sticky=tk.W)
        Button(self.labelframe_z3, text="Pickup Tip @", style="Default.TButton",
               command=lambda: self.test_pickup_tip()).grid(row=1, padx=10, pady=15, sticky=tk.W)
        Button(self.labelframe_z3, text="Aspirate", style="Default.TButton",
               command=lambda: self.test_aspirate()).grid(row=2, padx=10, pady=15, sticky=tk.W)
        Button(self.labelframe_z3, text="Dispense", style="Default.TButton",
               command=lambda: self.test_dispense()).grid(row=3, padx=10, pady=15, sticky=tk.W)
        Button(self.labelframe_z3, text="Eject Tip", style="Default.TButton",
               command=lambda: self.test_eject_tip()).grid(row=4, padx=10, pady=15, sticky=tk.W)
        self.current_tip = chem_robot.deck.get_current_tip()
        self.tip_frame = tk.Frame(self.labelframe_z3)
        self.tip_frame.grid(column=1, row=1, sticky=tk.N)
        slot_list = chem_robot.deck.get_vial_list_by_plate_type(
            plate_type="tiprack_1000uL")
        col_row = chem_robot.deck.get_cols_rows_by_plate_type(
            plate_type="tiprack_1000uL")
        self.tip_selection = custom_widgets.Item_selection_popup(
            parent=self.tip_frame, title="Current Tip:  ", slot_list=slot_list, COLS=col_row["columns"], ROWS=col_row["rows"], current=self.current_tip)

    def move_to_plate(self, head):
        slot = self.slot_selection.get_current(format="A1")
        vial = self.vial_selection.get_current(format="A1")
        vial_to = (slot, vial)
        chem_robot.move_to(head=head, vial=vial_to)

    def test_decap(self):
        slot = self.slot_selection.get_current(format="A1")
        vial = self.vial_selection.get_current(format="A1")
        vial_to = (slot, vial)
        chem_robot.decap(vial=vial_to)

    def test_recap(self):
        slot = self.slot_selection.get_current(format="A1")
        vial = self.vial_selection.get_current(format="A1")
        vial_to = (slot, vial)
        chem_robot.recap(vial=vial_to)

    def test_pickup_cap(self):
        cap_no = self.cap_selection.get_current(format="A1")
        cap_plate = chem_robot.deck.get_plate_assignment("Reaction caps")
        chem_robot.pickup_cap((cap_plate, cap_no))

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
        tip_no = self.tip_selection.get_current(format="A1")
        tip_plate = chem_robot.deck.get_plate_assignment("Tips 1000uL")
        chem_robot.pickup_tip((tip_plate, tip_no))

    def test_aspirate(self):
        volume = simpledialog.askfloat(
            'Volume', 'Please enter aspirate volume (mL)')
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


class Deck_tab(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        Label(self, text="Deck Setup", style="Title.Label").grid(
            column=2, row=0, padx=50, pady=30)
        self.slot_list = chem_robot.deck.slot_list
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
        COLS = 5
        ROWS = 3
        i = 0
        self.deck_frame = tk.LabelFrame(
            self, text="  Deck  ", fg="RoyalBlue4", font="Helvetica 11 bold")
        self.deck_frame.grid(column=0, columnspan=5, row=10,
                             padx=20, pady=20, sticky=tk.W)
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
                if assignment in ["Reactor", "Workup", "Trash", "Tips 1000uL"]:
                    btn.configure(style="Plate_r.TButton")
                btn.grid(row=row+2, column=col, pady=25, padx=20)
                self.btn_list.append(btn)
                i = i+1

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
        slot = self.config[x]["slot"]
        plate_type = self.config[x]["plate_type"]
        plate_no = self.config[x]["plate_no"]
        assignmnent = self.config[x]["assignment"]
        text = f"{slot}\n{plate_type} : {plate_no}\n{assignmnent}"
        self.btn_list[x].configure(text=text)


class Synthesis_tab(ttk.Frame):

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)

        Label(self, text=" Reaction Setup ", style="Title.Label").grid(
            column=0, columnspan=4, row=0, padx=20, pady=5)

        ip_address = socket.gethostbyname(socket.gethostname())
        Label(self, text="Enter your reaction protocol below, you may also upload your protocol via IP address: " +
              ip_address, style="Default.Label").grid(column=0, columnspan=4, row=1, padx=15, pady=5, sticky=tk.W)

        # Reaction plan editor
        self.plan_box = scrolledtext.ScrolledText(self, width=160, height=15)
        self.plan_box.grid(column=0, rowspan=4, padx=15, columnspan=4, row=3)
        self.display_plan(NEW_PLAN_HEADER)
        self.is_excel = False
        self.plan_file_name = "blank-plan"

        # Solvent option
        self.solvent_frame = tk.Frame(self)
        self.solvent_frame.grid(column=0, row=11, sticky=tk.N)
        Label(self.solvent_frame, text="Solvent option",
              style="Default.Label").grid(row=0, pady=5)
        self.solvent_addition_last = tk.IntVar()
        ttk.Checkbutton(self.solvent_frame, text="Add the below solvent at last",
                        variable=self.solvent_addition_last).grid(row=2, sticky=tk.W)
        Label(self.solvent_frame, text=" ").grid(row=3, sticky=tk.W)
        Label(self.solvent_frame, style="Default.Label",
              text="Solvent name:").grid(row=5, sticky=tk.W)
        self.solvent_selection = ttk.Combobox(
            self.solvent_frame, font=('Helvetica', '11'), width=20)
        self.solvent_selection["values"] = (
            "", "Water", "DCM", "MeOH", "Ethyl-acetate", "Hexanes", "Toluene", "THF", "DCE", "Dioxane", "Acetone")
        self.solvent_selection.current(0)  # set the selected item
        self.solvent_selection.grid(row=6, pady=5, sticky=tk.W)
        Label(self.solvent_frame, style="Default.Label",
              text="Solvent volume (mL):").grid(row=7, sticky=tk.W)
        self.volume_entry = ttk.Entry(self.solvent_frame, width=22,
                                      font=('Helvetica', '11'))
        self.volume_entry.grid(row=8, pady=2, sticky=tk.W)

        # Cap option
        self.cap_frame = tk.Frame(self)
        self.cap_frame.grid(column=1, row=11, sticky=tk.N)
        Label(self.cap_frame, text="Cap option",
              style="Default.Label").grid(row=0, pady=5)
        self.reactor_no_capping = tk.IntVar()
        ttk.Checkbutton(self.cap_frame, text="Not cap the reactor",
                        variable=self.reactor_no_capping).grid(row=3, sticky=tk.W)

        # Tip selector
        self.tip_frame = tk.Frame(self)
        self.tip_frame.grid(column=2, row=11, sticky=tk.N)
        self.current_tip = chem_robot.deck.get_current_tip()
        Label(self.tip_frame, text="Select starting tip",
              style="Default.Label").grid(row=0, pady=5)
        slot_list = chem_robot.deck.get_vial_list_by_plate_type(
            plate_type="tiprack_1000uL")
        col_row = chem_robot.deck.get_cols_rows_by_plate_type(
            plate_type="tiprack_1000uL")
        self.tip_selection = custom_widgets.Item_selection_popup(
            parent=self.tip_frame, title="Current Tip:  ", slot_list=slot_list, COLS=col_row["columns"], ROWS=col_row["rows"], current=self.current_tip)

        # Reactor selector
        self.reactor_frame = tk.Frame(self)
        self.reactor_frame.grid(column=3, row=11, sticky=tk.N)
        Label(self.reactor_frame, text="Select starting reactor",
              style="Default.Label").grid(row=0, pady=5)
        slot_list = chem_robot.deck.get_vial_list_by_plate_type(
            plate_type="plate_8mL")
        col_row = chem_robot.deck.get_cols_rows_by_plate_type(
            plate_type="plate_8mL")
        self.reactor_selection_frame = tk.Frame(
            self.reactor_frame, relief="ridge", bg="gray")
        self.reactor_selection_frame.grid(row=1)
        self.reactor_selection = custom_widgets.Item_selection_on_screen(
            parent=self.reactor_selection_frame, slot_list=slot_list, COLS=col_row["columns"], ROWS=col_row["rows"], current=0)

        # Display information
        self.display_frame = tk.Frame(self)
        self.display_frame.grid(column=0, rowspan=6, columnspan=4,
                                row=20, padx=15, pady=10)
        self.information = custom_widgets.Information_display(
            self.display_frame, title="Parsed reaction protocol will be shown here:\n", width=160, height=15)

        # Parse, run and stop buttons
        self.parse_button = Button(
            self, text="Parse reaction protocol", style="Green.TButton", command=lambda: self.parse())
        self.parse_button.grid(column=0, row=30, pady=10)
        self.run_button = Button(
            self, text="Run simulation", style="Green.TButton", command=lambda: self.run_simulation())
        self.run_button.grid(column=1, row=30, pady=10)
        self.run_button = Button(
            self, text="Setup reactions", style="Green.TButton", command=lambda: self.run())
        self.run_button.grid(column=2, row=30, pady=10)
        self.stop_button = Button(
            self, text="Stop running", style="Red.TButton", command=lambda: self.stop_reaction())
        self.stop_button.grid(column=3, row=30, pady=10)
        self.run_button["state"] = "disabled"

    def setup_reaction(self, tip=0, simulation=False):
        # chem_robot.pipette.initialization()
        reactor_no_cap = self.reactor_no_capping.get()
        solvent_last = self.solvent_addition_last.get()
        if solvent_last == 1:
            solvent_volume_string = self.volume_entry.get()
            solvent_name = self.solvent_selection.get()
            if solvent_name == "":
                messagebox.showinfo(" ", "Please enter a valid solvent nameL!")
                return
            if not helper.is_float(solvent_volume_string):
                messagebox.showinfo(" ", "Please enter solvent volume in mL!")
                return
            solvent_volume = float(solvent_volume_string)
            solvent_info = chem_synthesis.locate_reagent(solvent_name)
            if "not found" in solvent_info:
                messagebox.showinfo(" ", solvent_info)
                return
            else:
                solvent_plate_name = solvent_info["plate"]
                solvent_pos = solvent_info["vial"]

        if not chem_robot.ready:
            simulation = True
        missing = chem_robot.deck.check_missing_assignment()
        ok = messagebox.askokcancel(
            "Warning", f"Please make sure:\n 1) Reactor vials are uncapped.\n 2) Enough caps are put on cap plate (from A1). \n 3) All reagent vials are secured in the plate.")
        if not ok:
            return
        missing = chem_robot.deck.check_missing_assignment()
        if missing != "complete":
            retry = messagebox.askyesno(
                "Warning", f"Warning: No {missing} plate is assigned, continue?.")
            if not retry:
                return
        chem_robot.set_stop_flag(stop=False)
        if simulation:
            self.information.display_msg(
                "Robot not ready, run in the simulation mode:\n")
            time.sleep(1)
        else:
            self.information.display_msg("Starting running...")
        tip_no = self.tip_selection.get_current(format="A1")
        tip_plate = chem_robot.deck.get_plate_assignment("Tips 1000uL")

        cap_no = 'A1'
        cap_plate = chem_robot.deck.get_plate_assignment("Reaction caps")

        reactor_no = self.reactor_selection.get_current(format="A1")
        reactor_plate = chem_robot.deck.get_plate_assignment("Reactor")
        reactor_no_start = reactor_no
        reactor_start_number = self.reactor_selection.get_current()

        trash_plate = chem_robot.deck.get_plate_assignment("Trash")
        trash = (trash_plate, 'A1')

        clean_up_plate = chem_robot.deck.get_plate_assignment("Clean up")
        clean_up_position = chem_robot.deck.convert_number_to_A1(
            random.randint(1, 95), plate=clean_up_plate)
        clean_up = (clean_up_plate, clean_up_position)

        with open(Path("user_files/reactions.json")) as rxn_data:
            rxn = json.load(rxn_data)
        i = 1
        number_of_reaction = len(rxn)
        for entry in rxn:  # each entry is a reaction as dict
            if chem_robot.stop_flag:
                print("Stop")
                return ("stopped by user")
            tracking_number = entry["tracking_number"]
            output_msg = f"\nSetup reaction No. {i} of {number_of_reaction}, (tracking number: {tracking_number})"
            self.information.display_msg(output_msg, start_over=False)
            i = i+1
            reactor_vial = (reactor_plate, reactor_no)

            reagent_list = entry["reagents"]
            for reagent in reagent_list:
                if chem_robot.stop_flag:
                    return ("stopped by user")
                reagent_type = reagent["type"]
                reagent_name = reagent["name"]
                reagent_plate = chem_robot.deck.get_slot_from_plate_name(
                    reagent["plate"])
                reagent_location = reagent["position"]
                reagent_vial = (reagent_plate, reagent_location)
                reagent_amount = reagent["amount"]
                output_msg = f'Transfer {reagent_name} ({reagent_type}) from vial@ ({reagent_plate}, {reagent_location}), amount: {reagent_amount} (mL or tablet) to reactor@ {reactor_no} ...'
                self.information.display_msg(output_msg, start_over=False)
                if not simulation:
                    if reagent_type == "pure_liquid" or reagent_type == "solution":
                        if chem_robot.stop_flag:
                            return
                        tip = (tip_plate, tip_no)
                        while not chem_robot.decap(reagent_vial):
                            retry = messagebox.askyesno(
                                "Infomation", "Cap can't be opened, retry?")
                            if not retry:
                                return
                        chem_robot.transfer_liquid(vial_from=reagent_vial, vial_to=reactor_vial,
                                                   tip=tip, trash=trash, volume=reagent_amount)
                        chem_robot.recap(reagent_vial)
                        # change to next tip
                        tip_no = chem_robot.deck.next_vial(
                            tip_no, plate=tip_plate)
                        self.tip_selection.next()
                        chem_robot.deck.set_current_tip(
                            self.tip_selection.get_current())
                        chem_robot.deck.save_current_tip()

                    if reagent_type == "solid":
                        if chem_robot.stop_flag:
                            return
                        while not chem_robot.decap(reagent_vial):
                            retry = messagebox.askyesno(
                                "Infomation", "Cap can't be opened, retry?")
                            if not retry:
                                return
                        chem_robot.transfer_tablet(vial_from=reagent_vial, vial_to=reactor_vial,
                                                   number_of_tablet=reagent_amount)
                        if chem_robot.stop_flag:
                            return
                        chem_robot.recap(reagent_vial)
                        if chem_robot.stop_flag:
                            return
                        print(clean_up)
                        chem_robot.clean_up_needle(clean_up)
                        if chem_robot.stop_flag:
                            return
                else:
                    time.sleep(1)
                    if reagent_type == "pure_liquid" or reagent_type == "solution":
                        # change to next tip
                        tip_no = chem_robot.deck.next_vial(
                            tip_no, plate=tip_plate)
                        self.tip_selection.next()
                        chem_robot.deck.set_current_tip(
                            self.tip_selection.get_current())
                        chem_robot.deck.save_current_tip()

            if chem_robot.stop_flag:
                return

            # skip capping if reactor No cap box is checked
            if not simulation and reactor_no_cap == 0 and solvent_last == 0:
                chem_robot.pickup_cap((cap_plate, cap_no))
                if chem_robot.stop_flag:
                    return
                cap_no = chem_robot.deck.next_vial(
                    cap_no, plate=cap_plate)
                chem_robot.recap(reactor_vial)
                if chem_robot.stop_flag:
                    return
            reactor_no = chem_robot.deck.next_vial(
                reactor_no, plate=reactor_plate)
            self.reactor_selection.next()

        # Add the solvent in the last step
        if solvent_last == 1:
            solvent_slot = chem_robot.deck.get_slot_from_plate_name(
                solvent_plate_name)
            solvent_vial = (solvent_slot, solvent_pos)
            tip = (tip_plate, tip_no)
            if not simulation:
                chem_robot.pickup_tip(tip)
            if not simulation:
                chem_robot.decap(solvent_vial)
            if chem_robot.stop_flag:
                return ("stopped by user")

            # adding solvent
            self.information.display_msg(
                "\nSetup reaction competed, starting to add the last solvent\n", start_over=False)
            reactor_no = reactor_no_start
            self.reactor_selection.set_current(reactor_start_number)
            self.reactor_selection.next(0)
            i = 0
            for i in range(number_of_reaction):
                reactor_vial = (reactor_plate, reactor_no)
                if chem_robot.stop_flag:
                    return ("stopped by user")
                message = f"Run {i+1} of {number_of_reaction}, adding solvent {solvent_name} {solvent_volume} mL to reactor at {reactor_vial[1]} using tip {tip[1]}"
                self.information.display_msg(message, start_over=False)
                if not simulation:
                    chem_robot.transfer_liquid(vial_from=solvent_vial, vial_to=reactor_vial,
                                               tip=None, trash=trash, volume=solvent_volume)
                else:
                    time.sleep(1)
                reactor_no = chem_robot.deck.next_vial(
                    reactor_no, plate=reactor_plate)
                self.reactor_selection.next()
            if chem_robot.stop_flag:
                return ("stopped by user")
            if not simulation:
                chem_robot.drop_tip(trash)
            if chem_robot.stop_flag:
                return ("stopped by user")
            if not simulation:
                chem_robot.recap(solvent_vial)
            self.tip_selection.next()

            # adding cap
            if reactor_no_cap == 0:
                self.information.display_msg(
                    "\nSetup reaction competed, starting to add cap\n", start_over=False)
                reactor_no = reactor_no_start
                self.reactor_selection.set_current(reactor_start_number)
                self.reactor_selection.next(0)
                i = 0
                for i in range(number_of_reaction):
                    reactor_vial = (reactor_plate, reactor_no)
                    if chem_robot.stop_flag:
                        return ("stopped by user")
                    message = f"Run {i+1} of {number_of_reaction}, adding cap to reactor at {reactor_vial[1]}"
                    self.information.display_msg(message, start_over=False)
                    chem_robot.pickup_cap((cap_plate, cap_no))
                    chem_robot.recap(reactor_vial)

                    cap_no = chem_robot.deck.next_vial(cap_no, plate=cap_plate)
                    reactor_no = chem_robot.deck.next_vial(
                        reactor_no, plate=reactor_plate)
                    self.reactor_selection.next()
                    reactor_no = chem_robot.deck.next_vial(
                        reactor_no, plate=reactor_plate)
                    self.reactor_selection.next()

        self.run_button["state"] = "normal"
        self.update()
        self.information.display_msg(
            "\nFinished....................................................\n", start_over=False)
        chem_robot.deck.set_current_tip(self.tip_selection.get_current())
        chem_robot.deck.save_current_tip()

    def clean_up_after_stop(self):
        chem_robot.z_platform.home()

    def run(self):
        if chem_synthesis.ready:
            self.run_button["state"] = "disabled"
            self.update()
            t = threading.Thread(target=self.setup_reaction)
            t.start()
            self.run_button["state"] = "enabled"
            self.update()
        else:
            self.information.display_msg("Please load your reaction protocol.")

    def run_simulation(self):
        if chem_synthesis.ready:
            t = threading.Thread(target=self.setup_reaction(simulation=True))
            t.start()
        else:
            self.information.display_msg("Please load your reaction protocol.")

    def stop_reaction(self):
        chem_robot.set_stop_flag(stop=True)
        self.information.display_msg("Stopping......\n", start_over=False)
        self.run_button["state"] = "normal"
        self.update()
        chem_robot.home_all_z()
        chem_robot.pipette.initialization()
        chem_robot.gripper.initialization()
        chem_robot.set_stop_flag(stop=False)

    def display_plan(self, msg):
        self.plan_box.delete(1.0, tk.END)
        self.plan_box.insert(tk.INSERT, msg)
        self.plan_box.see("end")
        self.update()

    def open_reagent_index(self):
        filename = filedialog.askopenfilename(title="Select protocol file", filetypes=(
            ("excel file", "*.xlsx"), ("all files", "*.*")))
        chem_synthesis.load_reagent_index(filename)

    def open_plan(self):
        filename = filedialog.askopenfilename(title="Select protocol file", filetypes=(
            ("txt files", "*.txt"), ("all files", "*.*")))
        plan = open(filename, "r")
        string = plan.read()
        self.display_plan(string)
        chem_synthesis.ready = True
        # self.run_button["state"] = "normal"
        self.update()
        self.plan_file_name = filename
        self.is_excel = False

    def new_plan(self):
        filename = filedialog.asksaveasfilename(title="Name your plan file", filetypes=(
            ("txt files", "*.txt"), ("all files", "*.*")))
        if filename == "":
            return
        self.plan_file_name = filename + '.txt'
        self.display_plan(NEW_PLAN_HEADER)
        chem_synthesis.ready = True
        # self.run_button["state"] = "normal"
        self.update()
        self.is_excel = False

    def save_plan(self):
        self.parse()

    def save_as_plan(self):
        filename = filedialog.asksaveasfilename(title="Name your plan file", filetypes=(
            ("txt files", "*.txt"), ("all files", "*.*")))
        if filename == "":
            return
        self.plan_file_name = filename + '.txt'
        chem_synthesis.ready = True
        # self.run_button["state"] = "normal"
        self.update()
        self.is_excel = False
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
        print(self.plan_file_name)

    def parse(self):
        if not self.is_excel:
            self.plan_txt = self.plan_box.get("1.0", tk.END)
            # print(self.plan_txt)
            with open(self.plan_file_name, 'w') as output:
                output.write(self.plan_txt)
            # reactor_No = self.combo_reactor.get()
            res = chem_synthesis.load_synthesis_plan(self.plan_file_name)
            if "not found" in res:
                messagebox.showinfo(" ", res)
                return
            save_file_name = self.plan_file_name.split('.')[0] + '_run.txt'
            chem_synthesis.save_plan(
                save_file=save_file_name, reactor_starting_nubmer=1)
            with open(Path("user_files/reactions.json"), 'r') as output:
                parsed_plan = output.read()
            self.information.display_msg(parsed_plan)
            chem_synthesis.ready = True
            self.run_button["state"] = "enabled"
        else:
            res = chem_synthesis.load_synthesis_plan_excel(self.plan_file_name)
            if "not found" in res:
                messagebox.showinfo(" ", res)
                return
            save_file_name = self.plan_file_name.split('.')[0] + '_run.txt'
            chem_synthesis.save_plan(
                save_file=save_file_name, reactor_starting_nubmer=1)
            with open(Path("user_files/reactions.json"), 'r') as output:
                parsed_plan = output.read()
            self.information.display_msg(parsed_plan)
            chem_synthesis.ready = True
            self.run_button["state"] = "enabled"


class Monitor_tab(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        # Title
        Label(self, text=" Reaction Monitor ", style="Title.Label").grid(
            column=0, columnspan=4, row=0, padx=20, pady=5)

        # Tip selector
        current_tip = chem_robot.deck.get_current_tip()
        Label(self, text="Select starting tip",
              style="Default.Label").grid(column=0, row=4, pady=5)
        self.tip_frame = tk.Frame(self)
        self.tip_frame.grid(column=0, row=6, sticky=tk.N)
        slot_list = chem_robot.deck.get_vial_list_by_plate_type(
            plate_type="tiprack_1000uL")
        col_row = chem_robot.deck.get_cols_rows_by_plate_type(
            plate_type="tiprack_1000uL")
        self.tip_selection = custom_widgets.Item_selection_popup(
            parent=self.tip_frame, title="Current Tip:  ", slot_list=slot_list, COLS=col_row["columns"], ROWS=col_row["rows"], current=current_tip)

        # Reactor selector
        Label(self, text="Select starting reactor",
              style="Default.Label").grid(column=1, row=4, pady=5)
        self.reactor_frame = tk.Frame(self, relief="ridge", bg="gray")
        self.reactor_frame.grid(column=1, row=6, sticky=tk.N)
        slot_list = chem_robot.deck.get_vial_list_by_plate_type(
            plate_type="plate_8mL")
        col_row = chem_robot.deck.get_cols_rows_by_plate_type(
            plate_type="plate_8mL")
        self.reactor_selection = custom_widgets.Item_selection_on_screen(
            parent=self.reactor_frame, slot_list=slot_list, COLS=col_row["columns"], ROWS=col_row["rows"], current=0)

        # GC-LC vial selector
        Label(self, text="Select starting GC/LC vial",
              style="Default.Label").grid(column=2, row=4, padx=5)
        self.GC_LC_frame = tk.Frame(self, relief="ridge", bg="gray")
        self.GC_LC_frame.grid(column=2, row=6, sticky=tk.N)
        slot_list = chem_robot.deck.get_vial_list_by_plate_type(
            plate_type="plate_2mL")
        col_row = chem_robot.deck.get_cols_rows_by_plate_type(
            plate_type="plate_2mL")
        self.GC_LC_selection = custom_widgets.Item_selection_on_screen(
            parent=self.GC_LC_frame, slot_list=slot_list, COLS=col_row["columns"], ROWS=col_row["rows"], current=0)

        # Number of reactions selection
        self.number_frame = tk.LabelFrame(
            self, text="Number of reactions", fg="RoyalBlue4", font="Helvetica 11 bold")
        self.number_frame.grid(column=0, row=9, padx=15, pady=10, sticky=tk.NW)
        self.number_reaction = ttk.Combobox(
            self.number_frame, state="readonly", font=('Helvetica', '11'))
        self.number_reaction["values"] = (
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
        self.number_reaction.current(0)  # set the selected item
        self.number_reaction.grid(pady=5)

        # Sampling volume selector
        options = [{"text": "2 uL", "value": 2.0},
                   {"text": "5 uL", "value": 5.0},
                   {"text": "10 uL", "value": 10.0}
                   ]
        self.sampling_volume_frame = tk.Frame(self, relief="ridge", bg="gray")
        self.sampling_volume_frame.grid(column=1, row=9, pady=10, sticky=tk.N)
        self.sampling_volume_selection = custom_widgets.Volume_selection(
            parent=self.sampling_volume_frame, title="Reaction volume (mL)", options=options)

        # Solvent type selection
        self.solvent_frame = tk.LabelFrame(
            self, text="Solvent for dilution", fg="RoyalBlue4", font="Helvetica 11 bold")
        self.solvent_frame.grid(column=2, row=9, pady=10, sticky=tk.N)
        self.solvent_selection = ttk.Combobox(
            self.solvent_frame, font=('Helvetica', '11'))
        self.solvent_selection["values"] = (
            "DCM", "MeOH", "Ethyl-acetate", "Hexanes")
        self.solvent_selection.current(0)  # set the selected item
        self.solvent_selection.grid(pady=5)

        # Dilution solvent volume selection
        options = [{"text": "0.3 mL", "value": 0.3},
                   {"text": "0.6 mL", "value": 0.6},
                   {"text": "1.0 mL", "value": 1.0}
                   ]
        self.dilution_volume_frame = tk.Frame(self, relief="ridge", bg="gray")
        self.dilution_volume_frame.grid(column=3, row=9, pady=10, sticky=tk.N)
        self.dilution_volume_selection = custom_widgets.Volume_selection(
            parent=self.dilution_volume_frame, title="Dilution solvent volume (mL)", options=options)

        # Display information
        self.display_frame = tk.Frame(self)
        self.display_frame.grid(column=0, rowspan=6, columnspan=4,
                                row=50, padx=15, pady=10)
        self.information = custom_widgets.Information_display(
            self.display_frame, title="Progress:", width=160, height=15)

        # Run and stop buttons
        self.run_button = Button(
            self, text="Start sampling", style="Green.TButton", command=lambda: self.run())
        self.run_button.grid(column=0, row=60, padx=10, pady=10)
        self.stop_button = Button(
            self, text="Stop running", style="Red.TButton", command=lambda: self.stop())
        self.stop_button.grid(column=1, row=60, padx=10, pady=10)

    def monitor_reaction(self, simulation=False):
        chem_robot.set_stop_flag(stop=False)

        if not chem_robot.ready:
            simulation = True
            self.information.display_msg(
                "Robot not ready, run in the simulation mode:\n")
            time.sleep(1)
        else:
            self.information.display_msg("Start sampling...\n")

        tip_no = self.tip_selection.get_current(format="A1")
        tip_plate = chem_robot.deck.get_plate_assignment("Tips 1000uL")

        reactor_no = self.reactor_selection.get_current(format="A1")
        reactor_plate = chem_robot.deck.get_plate_assignment("Reactor")

        trash_plate = chem_robot.deck.get_plate_assignment("Trash")
        trash = (trash_plate, 'A1')

        GC_LC_plate = chem_robot.deck.get_plate_assignment("GC LC")
        GC_LC_no = self.GC_LC_selection.get_current(format="A1")

        GC_LC_start_number = self.GC_LC_selection.get_current()
        GC_LC_no_start = GC_LC_no

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
        for i in range(number_of_reaction):
            if chem_robot.stop_flag:
                return ("stopped by user")

            reactor_vial = (reactor_plate, reactor_no)
            reactor_no = chem_robot.deck.next_vial(
                reactor_no, plate=reactor_plate)
            self.reactor_selection.next()

            GC_LC_vial = (GC_LC_plate, GC_LC_no)
            GC_LC_no = chem_robot.deck.next_vial(GC_LC_no, plate=GC_LC_plate)
            self.GC_LC_selection.next()

            tip = (tip_plate, tip_no)

            sample_volume = self.sampling_volume_selection.get_value()/1000  # uL convert to mL
            dilution_volume = self.dilution_volume_selection.get_value()  # in mL already

            message = f"Run {i+1} of {number_of_reaction}, sampling {sample_volume} mL from reactor {reactor_vial[1]} to GC/LC vial at {GC_LC_vial[1]} using tip {tip[1]}"
            self.information.display_msg(message, start_over=False)

            if simulation:
                time.sleep(1)  # run in the simulation mode
            else:
                if chem_robot.stop_flag:
                    return ("stopped by user")
                chem_robot.decap(reactor_vial)
                if chem_robot.stop_flag:
                    return ("stopped by user")
                chem_robot.transfer_liquid(vial_from=reactor_vial, vial_to=GC_LC_vial,
                                           tip=tip, trash=trash, volume=sample_volume)
                if chem_robot.stop_flag:
                    return ("stopped by user")
                chem_robot.recap(reactor_vial)
                if chem_robot.stop_flag:
                    return ("stopped by user")
            tip_no = chem_robot.deck.next_vial(tip_no, plate=tip_plate)
            self.tip_selection.next()
            chem_robot.deck.set_current_tip(self.tip_selection.get_current())

        if chem_robot.stop_flag:
            return ("stopped by user")

        # Add dilution solvent for each GC-LC vials
        tip = (tip_plate, tip_no)
        if not simulation:
            chem_robot.pickup_tip(tip)
        if not simulation:
            chem_robot.decap(solvent_vial)
        if chem_robot.stop_flag:
            return ("stopped by user")
        GC_LC_no = GC_LC_no_start
        self.GC_LC_selection.set_current(GC_LC_start_number)
        self.GC_LC_selection.next(0)

        self.information.display_msg(
            "\nSampling competed, starting to add dilution solvent\n", start_over=False)
        for i in range(number_of_reaction):
            GC_LC_vial = (GC_LC_plate, GC_LC_no)
            if chem_robot.stop_flag:
                return ("stopped by user")
            message = f"Run {i+1} of {number_of_reaction}, adding dilution solvent {solvent_name} {dilution_volume} mL to GC/LC vial at {GC_LC_vial[1]} using tip {tip[1]}"
            self.information.display_msg(message, start_over=False)
            if not simulation:
                chem_robot.transfer_liquid(vial_from=solvent_vial, vial_to=GC_LC_vial,
                                           tip=None, trash=trash, volume=dilution_volume)
            else:
                time.sleep(1)
            GC_LC_no = chem_robot.deck.next_vial(GC_LC_no, plate=GC_LC_plate)
            self.GC_LC_selection.next()

        if chem_robot.stop_flag:
            return ("stopped by user")
        if not simulation:
            chem_robot.drop_tip(trash)
        if chem_robot.stop_flag:
            return ("stopped by user")
        if not simulation:
            chem_robot.recap(solvent_vial)
        self.tip_selection.next()
        chem_robot.deck.set_current_tip(self.tip_selection.get_current())
        self.information.display_msg(
            "\nFinished....................................................\n", start_over=False)
        chem_robot.deck.save_current_tip()

    def run(self):
        self.run_button["state"] = "disabled"
        self.update()
        t = threading.Thread(target=self.monitor_reaction)
        t.start()
        self.run_button["state"] = "enabled"
        self.update()

    def stop(self):
        chem_robot.set_stop_flag(stop=True)
        self.information.display_msg("Stopping......\n", start_over=False)
        self.run_button["state"] = "normal"
        self.update()
        chem_robot.home_all_z()


class Workup_tab(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)

        Label(self, text="Reaction Workup", style="Title.Label").grid(
            column=0, columnspan=4, row=0, pady=20)

        # Tip selector
        current_tip = chem_robot.deck.get_current_tip()
        Label(self, text="Select starting tip",
              style="Default.Label").grid(column=0, row=4, pady=5)
        self.tip_frame = tk.Frame(self)
        self.tip_frame.grid(column=0, row=6, sticky=tk.N)
        slot_list = chem_robot.deck.get_vial_list_by_plate_type(
            plate_type="tiprack_1000uL")
        col_row = chem_robot.deck.get_cols_rows_by_plate_type(
            plate_type="tiprack_1000uL")
        self.tip_selection = custom_widgets.Item_selection_popup(
            parent=self.tip_frame, title="Current Tip:  ", slot_list=slot_list, COLS=col_row["columns"], ROWS=col_row["rows"], current=current_tip)

        # Reactor selector
        Label(self, text="Select starting reactor",
              style="Default.Label").grid(column=1, row=4, pady=5)
        self.reactor_frame = tk.Frame(self, relief="ridge", bg="gray")
        self.reactor_frame.grid(column=1, row=6)
        slot_list = chem_robot.deck.get_vial_list_by_plate_type(
            plate_type="plate_8mL")
        cols = chem_robot.deck.get_cols_rows_by_plate_type(
            plate_type="plate_8mL")["columns"]
        rows = chem_robot.deck.get_cols_rows_by_plate_type(
            plate_type="plate_8mL")["rows"]
        self.reactor_selection = custom_widgets.Item_selection_on_screen(
            parent=self.reactor_frame, slot_list=slot_list, COLS=cols, ROWS=rows, current=0)

        # Workup cartridge selector
        Label(self, text="Select starting workup cartridge",
              style="Default.Label").grid(column=2, row=4, padx=5)
        self.workup_frame = tk.Frame(self, relief="ridge", bg="gray")
        self.workup_frame.grid(column=2, row=6)
        slot_list = chem_robot.deck.get_vial_list_by_plate_type(
            plate_type="workup_small")
        col_row = chem_robot.deck.get_cols_rows_by_plate_type(
            plate_type="workup_small")
        self.workup_selection = custom_widgets.Item_selection_on_screen(
            parent=self.workup_frame, slot_list=slot_list, COLS=col_row["columns"], ROWS=col_row["rows"], current=0)

        # Number of reactions selector
        self.number_frame = tk.LabelFrame(
            self, text="Number of reactions", fg="RoyalBlue4", font="Helvetica 11 bold")
        self.number_frame.grid(column=0, row=9, pady=20, sticky=tk.N)
        self.number_reaction = ttk.Combobox(
            self.number_frame, state="readonly", font=('Helvetica', '11'))
        self.number_reaction["values"] = (
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
        self.number_reaction.current(0)  # set the selected item
        self.number_reaction.grid(pady=5)

        # Reaction volume selector
        options = [{"text": "0.5 mL", "value": 0.5},
                   {"text": "1.0 mL", "value": 1.0},
                   {"text": "2.0 mL", "value": 2.0}
                   ]
        self.reaction_volume_frame = tk.Frame(self, relief="ridge", bg="gray")
        self.reaction_volume_frame.grid(column=1, row=9, pady=10, sticky=tk.N)
        self.reaction_volume_selection = custom_widgets.Volume_selection(
            parent=self.reaction_volume_frame, title="Reaction volume (mL)", options=options)

        # Display of information
        self.display_frame = tk.Frame(self, relief="ridge", bg="gray")
        self.display_frame.grid(column=0, rowspan=6, columnspan=4,
                                row=50, padx=15, pady=10)
        self.information = custom_widgets.Information_display(
            self.display_frame, title="Progress shown", width=160, height=15)

        # Run, pause and stop buttons
        self.run_button = Button(
            self, text="Start work-up", style="Green.TButton", command=lambda: self.run())
        self.run_button.grid(column=0, row=60, padx=10, pady=10)

        self.stop_button = Button(
            self, text="Stop / Pause", style="Red.TButton", command=lambda: self.stop())
        self.stop_button.grid(column=1, row=60, padx=10, pady=10)

    def workup_reaction(self, simulation=False):
        '''main entry for workup'''
        chem_robot.set_stop_flag(stop=False)
        if not chem_robot.ready:
            simulation = True
            self.information.display_msg(
                "Robot not ready, run in the simulation mode:\n")
            time.sleep(1)
        else:
            self.information.display_msg("Start work-up...\n")

        tip_no = self.tip_selection.get_current(format="A1")
        tip_plate = chem_robot.deck.get_plate_assignment("Tips 1000uL")
        reactor_no = self.reactor_selection.get_current(format="A1")
        reactor_plate = chem_robot.deck.get_plate_assignment("Reactor")
        trash_plate = chem_robot.deck.get_plate_assignment("Trash")
        trash = (trash_plate, 'A1')
        workup_cartridge_plate = chem_robot.deck.get_plate_assignment("Workup")
        workup_cartridge_no = self.workup_selection.get_current(format="A1")
        number_of_reaction = int(self.number_reaction.get())

        available_tip = len(chem_robot.deck.get_vial_list_by_plate_type(
            "tiprack_1000uL"))-self.tip_selection.get_current()
        available_reactor = len(chem_robot.deck.get_vial_list_by_plate_type(
            "plate_8mL"))-self.reactor_selection.get_current()
        available_workup_cartridge = len(chem_robot.deck.get_vial_list_by_plate_type(
            "workup_small"))-self.workup_selection.get_current()
        if available_tip < number_of_reaction:
            messagebox.showinfo(
                " ", "Warning: No enough tip, please refill tips from A1")
        if available_reactor < number_of_reaction:
            messagebox.showinfo(" ", "Warning: No enough reactor!")
            return
        if available_workup_cartridge < number_of_reaction:
            messagebox.showinfo(" ", "Warning: No enough reactor!")
            return

        for i in range(number_of_reaction):
            if self.check_stop_status() == "stop":
                return
            tip = (tip_plate, tip_no)
            reactor = (reactor_plate, reactor_no)
            workup_cartridge = (workup_cartridge_plate, workup_cartridge_no)

            reaction_volume = self.reaction_volume_selection.get_value()
            message = f"Run {i+1} of {number_of_reaction}, transfer {reaction_volume} mL reaction mixture from reactor@ {reactor[1]} to workup cartridge@ {workup_cartridge_no} using tip@ {tip[1]}"
            self.information.display_msg(message, start_over=False)
            if simulation:
                time.sleep(1)  # run in the simulation mode
            else:
                if self.check_stop_status() == "stop":
                    return
                chem_robot.decap(reactor)
                if self.check_stop_status() == "stop":
                    return
                chem_robot.transfer_liquid(vial_from=reactor, vial_to=workup_cartridge,
                                           tip=tip, trash=trash, volume=reaction_volume)
                if self.check_stop_status() == "stop":
                    return
                chem_robot.recap(reactor)
                if self.check_stop_status() == "stop":
                    return

            # Move to next item (tip, reactor...)
            reactor_no = chem_robot.deck.next_vial(
                reactor_no, plate=reactor_plate)
            workup_cartridge_no = chem_robot.deck.next_vial(
                workup_cartridge_no, plate=workup_cartridge_plate)
            tip_no = chem_robot.deck.next_vial(tip_no, plate=tip_plate)
            self.tip_selection.next()
            chem_robot.deck.set_current_tip(self.tip_selection.get_current())
            self.reactor_selection.next()
            self.workup_selection.next()

        self.information.display_msg(
            "\nFinished....................................................\n", start_over=False)
        chem_robot.deck.save_current_tip()

    def run(self):
        self.run_button["state"] = "disabled"
        self.update()
        t = threading.Thread(target=self.workup_reaction)
        t.start()
        self.run_button["state"] = "enabled"
        self.update()

    def stop(self):
        chem_robot.set_stop_flag(stop=True)
        self.information.display_msg("\nStopping......\n", start_over=False)
        self.run_button["state"] = "normal"
        self.update()

    def check_stop_status(self):
        if chem_robot.stop_flag:
            yes = tk.messagebox.askyesno(
                "Warning", "Are you sure want to stop?")
            if yes:
                return "stop"
            else:
                chem_robot.set_stop_flag(False)
                return "continue"


# This following is the pop-up windows used in the program

# Used in deck setup
class Slot_assignment():
    def __init__(self, slot):
        self.t = Toplevel()
        self.slots = slot
        self.t.title(slot["slot"])
        Label(self.t, text="Plate type").grid(column=0, row=0, padx=10, pady=5)
        Label(self.t, text="Plate serial No.").grid(
            column=1, row=0, padx=10, pady=5)

        self.plate_type = ttk.Combobox(self.t, width=15, state="readonly")
        plate_type_turple = ("plate_2mL", "plate_5mL", "plate_8mL", "plate_15mL", "plate_40mL",
                             "tiprack_1000uL", "tiprack_50uL", "workup_big", "workup_small", "trash", "clean_up", "caps", "not_used")
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
        assignment_dict = {
            "plate_5mL": "Reagent",
            "plate_8mL": "Reactor",
            "plate_15mL": "Reactor",
            "plate_40mL": "Reagent",
            "tiprack_1000uL": "Tips 1000uL",
            "tiprack_50uL": "Tips 50uL",
            "workup_big": "Workup",
            "workup_small": "Workup",
            "trash": "Trash",
            "clean_up": "Clean up",
            "caps": "Reaction caps",
            "not_used": "Not_used",
            "plate_2mL": "GC LC"
        }
        assignment = assignment_dict[plate_type]
        slot = self.slots["slot"]
        chem_robot.deck.deck_config[slot] = {
            "plate": plate_name, "assignment": assignment}
        chem_robot.deck.save_deck_config(chem_robot.deck.deck_config)
        self.t.destroy()

    def cancel(self):
        self.t.destroy()


# Plate Calibration, accessed from menu - calibration
class Plate_calibration(ttk.Frame):
    def __init__(self):
        self.popup_window = Toplevel()
        self.popup_window.title(" Plate Calibration ")

        # Slot selector
        move_botton = Button(self.popup_window, text="Move to selected slot @", style="Default.TButton",
                             command=lambda: self.move_to_plate())
        move_botton.grid(column=1, row=0, pady=5)
        self.current_slot = 5
        self.slot_frame = tk.Frame(
            self.popup_window, relief="ridge", bg="gray")
        self.slot_frame.grid(column=1, row=1, padx=10, rowspan=3)
        slot_list = chem_robot.deck.get_vial_list_by_plate_type(
            plate_type="deck")
        self.slot_selection = custom_widgets.Item_selection_on_screen(
            parent=self.slot_frame, slot_list=slot_list, COLS=5, ROWS=3, current=self.current_slot)

        Label(self.popup_window, text=" ").grid(column=1, row=7, padx=10, pady=10)
        # Move functions as an LabelFrame
        self.move_frame = tk.LabelFrame(
            self.popup_window, text="Move axies (X, Y, Z1, Z2, Z3)", fg="RoyalBlue4", font="Helvetica 11 bold")
        self.move_frame.grid(column=0, columnspan=4, row=10,
                             padx=20, pady=10, sticky=tk.W)
        self.move_axies = custom_widgets.Move_axes(parent=self.move_frame, robot = chem_robot)

        # Save buttons
        Label(self.popup_window, text=" ").grid(
            column=1, row=16, padx=10, pady=10)
        self.button_save = Button(self.popup_window, text="Save calibration", style="Red.TButton",
                                  command=lambda: self.save_calibration_plate())
        self.button_save.grid(column=1, row=20, padx=0, pady=10)
        self.button_save.focus_force()
        self.popup_window.grab_set()  # keep this pop window focused

        # Cancel buttons
        self.button_cancel = Button(self.popup_window, text="Cancel", style="Default.TButton",
                                  command=lambda: self.cancel())
        self.button_cancel.grid(column=2, row=20, padx=0, pady=10)

    def save_calibration_plate(self):
        # the smoothieware has a strange problem on max speed, I have to work around by double (*2) the steps_per_mm
        x = chem_robot.get_axe_position("x")
        y = chem_robot.get_axe_position("y")
        current_head = self.head_select.get()
        z = chem_robot.get_axe_position(current_head)
        plate_for_calibration = self.slot_selection.get_current(format="A1")
        coordinate_of_vial = chem_robot.deck.vial(plate=plate_for_calibration,
                                                  vial='A1')
        calibration_data = [x-coordinate_of_vial['x']-chem_robot.deck.head_offsets[current_head][0],
                            y-coordinate_of_vial['y']-chem_robot.deck.head_offsets[current_head][1],
                            z-coordinate_of_vial['z']]
        chem_robot.deck.save_calibration(plate=plate_for_calibration,
                                         calibration_data=calibration_data)
        chem_robot.update()

    def cancel(self):
        self.popup_window.destroy()

    def move_to_plate(self):
        slot = chem_robot.deck.get_vial_list_by_plate_type(
            plate_type="deck")[self.slot_selection.get_current()]
        vial_to = (slot, "A1")
        current_head = self.move_axies.get_current_head()
        chem_robot.move_to(head=current_head, vial=vial_to)


# Tip Calibration, accessed from menu - calibration
class Tip_calibration(ttk.Frame):
    def __init__(self):
        self.popup_window = Toplevel()
        self.popup_window.title(" Tip Calibration ")

        # Slot selector
        move_botton = Button(self.popup_window, text="Move to tip rack @", style="Default.TButton",
                             command=lambda: self.move_to_tip_rack())
        move_botton.grid(column=1, row=0, padx = 40, pady=5)
        # Label(self.popup_window, text=" ").grid(column=1, row=7, padx=10, pady=10)

        # Move functions as an LabelFrame
        self.move_frame = tk.LabelFrame(
            self.popup_window, text="Move axies (X, Y, Z1, Z2, Z3)", fg="RoyalBlue4", font="Helvetica 11 bold")
        self.move_frame.grid(column=0, columnspan=4, row=10,
                             padx=20, pady=10, sticky=tk.W)
        self.move_axies = custom_widgets.Move_axes(parent=self.move_frame, robot = chem_robot)

        # Save buttons
        Label(self.popup_window, text=" ").grid(
            column=1, row=16, padx=10, pady=10)
        self.button_save = Button(self.popup_window, text="Save calibration", style="Red.TButton",
                                  command=lambda: self.save_calibration_tip())
        self.button_save.grid(column=1, row=20, padx=0, pady=10)
        self.button_save.focus_force()
        self.popup_window.grab_set()  # keep this pop window focused

        # Cancel buttons
        self.button_cancel = Button(self.popup_window, text="Cancel", style="Default.TButton",
                                  command=lambda: self.cancel())
        self.button_cancel.grid(column=2, row=20, padx=0, pady=10)

    def save_calibration_tip(self, tip="Tips_1000uL"):
        ''' the Tips was considered as plate name for simiplicity '''
        z = chem_robot.get_axe_position(axe = LIQUID)
        # tip_plate_50 = chem_robot.deck.get_plate_assignment("Tips 50uL")
        # tip_plate_1000 = chem_robot.deck.get_plate_assignment("Tips 1000uL")
        chem_robot.deck.save_calibration(plate="Tips_1000uL",
                                             calibration_data=[0, 0, z])
        chem_robot.update()                                             

    def cancel(self):
        self.popup_window.destroy()

    def move_to_tip_rack(self):
        tip_plate_1000 = chem_robot.deck.get_plate_assignment("Tips 1000uL")
        vial_to = (tip_plate_1000, "A1")
        chem_robot.move_to(head=LIQUID, vial=vial_to)


# Used in reagent distrubution
class Reagent_distrubution():
    def __init__(self):
        self.t = Toplevel()
        self.t.title("Solvent distribution ")

        # Tip selector
        current_tip = chem_robot.deck.get_current_tip()
        Label(self.t, text="Select starting tip",
              style="Default.Label").grid(column=0, row=4, pady=5)
        self.tip_frame = tk.Frame(self.t)
        self.tip_frame.grid(column=0, row=6, sticky=tk.N)
        slot_list = chem_robot.deck.get_vial_list_by_plate_type(
            plate_type="tiprack_1000uL")
        col_row = chem_robot.deck.get_cols_rows_by_plate_type(
            plate_type="tiprack_1000uL")
        self.tip_selection = custom_widgets.Item_selection_popup(
            parent=self.tip_frame, title="Current Tip:  ", slot_list=slot_list, COLS=col_row["columns"], ROWS=col_row["rows"], current=current_tip)

        # Reactor selector
        Label(self.t, text="Select starting reactor",
              style="Default.Label").grid(column=1, row=4, pady=5)
        self.reactor_frame = tk.Frame(self.t, relief="ridge", bg="gray")
        self.reactor_frame.grid(column=1, row=6)
        slot_list = chem_robot.deck.get_vial_list_by_plate_type(
            plate_type="plate_8mL")
        cols = chem_robot.deck.get_cols_rows_by_plate_type(
            plate_type="plate_8mL")["columns"]
        rows = chem_robot.deck.get_cols_rows_by_plate_type(
            plate_type="plate_8mL")["rows"]
        self.reactor_selection = custom_widgets.Item_selection_on_screen(
            parent=self.reactor_frame, slot_list=slot_list, COLS=cols, ROWS=rows, current=0)

        # Number of reactions selector
        self.number_frame = tk.LabelFrame(
            self.t, text="Number of reactions", fg="RoyalBlue4", font="Helvetica 11 bold")
        self.number_frame.grid(column=0, row=9, pady=20, sticky=tk.N)
        self.number_reaction = ttk.Combobox(
            self.number_frame, state="readonly", font=('Helvetica', '11'))
        self.number_reaction["values"] = (
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
        self.number_reaction.current(0)  # set the selected item
        self.number_reaction.grid(pady=5)

        # Reaction volume selector
        options = [{"text": "0.5 mL", "value": 0.5},
                   {"text": "1.0 mL", "value": 1.0},
                   {"text": "2.0 mL", "value": 2.0}
                   ]
        self.reaction_volume_frame = tk.Frame(
            self.t, relief="ridge", bg="gray")
        self.reaction_volume_frame.grid(column=1, row=9, pady=10, sticky=tk.N)
        self.reaction_volume_selection = custom_widgets.Volume_selection(
            parent=self.reaction_volume_frame, title="Reaction volume (mL)", options=options)

        # Display of information
        self.display_frame = tk.Frame(self.t, relief="ridge", bg="gray")
        self.display_frame.grid(column=0, rowspan=6, columnspan=4,
                                row=50, padx=15, pady=10)
        self.information = custom_widgets.Information_display(
            self.display_frame, title="Progress shown", width=100, height=15)

        # Run, pause and stop buttons
        self.run_button = Button(
            self.t, text="Start work-up", style="Green.TButton", command=lambda: self.run())
        self.run_button.grid(column=0, row=60, padx=10, pady=10)

        self.stop_button = Button(
            self.t, text="Stop / Pause", style="Red.TButton", command=lambda: self.stop())
        self.stop_button.grid(column=1, row=60, padx=10, pady=10)
        self.run_button.focus_force()
        self.t.grab_set()  # keep this pop window focused

    def workup_reaction(self, simulation=False):
        '''main entry for workup'''
        chem_robot.set_stop_flag(stop=False)
        if not chem_robot.ready:
            simulation = True
            self.information.display_msg(
                "Robot not ready, run in the simulation mode:\n")
            time.sleep(1)
        else:
            self.information.display_msg("Start work-up...\n")

        tip_no = self.tip_selection.get_current(format="A1")
        tip_plate = chem_robot.deck.get_plate_assignment("Tips 1000uL")
        reactor_no = self.reactor_selection.get_current(format="A1")
        reactor_plate = chem_robot.deck.get_plate_assignment("Reactor")
        trash_plate = chem_robot.deck.get_plate_assignment("Trash")
        trash = (trash_plate, 'A1')
        workup_cartridge_plate = chem_robot.deck.get_plate_assignment("Workup")
        workup_cartridge_no = self.workup_selection.get_current(format="A1")
        number_of_reaction = int(self.number_reaction.get())

        available_tip = len(chem_robot.deck.get_vial_list_by_plate_type(
            "tiprack_1000uL"))-self.tip_selection.get_current()
        available_reactor = len(chem_robot.deck.get_vial_list_by_plate_type(
            "plate_8mL"))-self.reactor_selection.get_current()
        available_workup_cartridge = len(chem_robot.deck.get_vial_list_by_plate_type(
            "workup_small"))-self.workup_selection.get_current()
        if available_tip < number_of_reaction:
            messagebox.showinfo(
                " ", "Warning: No enough tip, please refill tips from A1")
        if available_reactor < number_of_reaction:
            messagebox.showinfo(" ", "Warning: No enough reactor!")
            return
        if available_workup_cartridge < number_of_reaction:
            messagebox.showinfo(" ", "Warning: No enough reactor!")
            return

        for i in range(number_of_reaction):
            if self.check_stop_status() == "stop":
                return
            tip = (tip_plate, tip_no)
            reactor = (reactor_plate, reactor_no)
            workup_cartridge = (workup_cartridge_plate, workup_cartridge_no)

            reaction_volume = self.reaction_volume_selection.get_value()
            message = f"Run {i+1} of {number_of_reaction}, transfer {reaction_volume} mL reaction mixture from reactor@ {reactor[1]} to workup cartridge@ {workup_cartridge_no} using tip@ {tip[1]}"
            self.information.display_msg(message, start_over=False)
            if simulation:
                time.sleep(1)  # run in the simulation mode
            else:
                if self.check_stop_status() == "stop":
                    return
                chem_robot.decap(reactor)
                if self.check_stop_status() == "stop":
                    return
                chem_robot.transfer_liquid(vial_from=reactor, vial_to=workup_cartridge,
                                           tip=tip, trash=trash, volume=reaction_volume)
                if self.check_stop_status() == "stop":
                    return
                chem_robot.recap(reactor)
                if self.check_stop_status() == "stop":
                    return

            # Move to next item (tip, reactor...)
            reactor_no = chem_robot.deck.next_vial(
                reactor_no, plate=reactor_plate)
            workup_cartridge_no = chem_robot.deck.next_vial(
                workup_cartridge_no, plate=workup_cartridge_plate)
            tip_no = chem_robot.deck.next_vial(tip_no, plate=tip_plate)
            self.tip_selection.next()
            chem_robot.deck.set_current_tip(self.tip_selection.get_current())
            self.reactor_selection.next()
            self.workup_selection.next()

        self.information.display_msg(
            "\nFinished....................................................\n", start_over=False)
        chem_robot.deck.save_current_tip()

    def run(self):
        self.run_button["state"] = "disabled"
        t = threading.Thread(target=self.workup_reaction)
        t.start()
        self.run_button["state"] = "enabled"

    def stop(self):
        chem_robot.set_stop_flag(stop=True)
        self.information.display_msg("\nStopping......\n", start_over=False)
        self.run_button["state"] = "normal"

    def check_stop_status(self):
        if chem_robot.stop_flag:
            yes = tk.messagebox.askyesno(
                "Warning", "Are you sure want to stop?")
            if yes:
                return "stop"
            else:
                chem_robot.set_stop_flag(False)
                return "continue"

    def save(self):
        plate_type = self.plate_type.get()
        plate_no = self.plate_serial.get()
        plate_name = plate_type + ":" + plate_no
        assignment_dict = {
            "plate_5mL": "Reagent",
            "plate_8mL": "Reactor",
            "plate_15mL": "Reactor",
            "plate_40mL": "Reagent",
            "tiprack_1000uL": "Tips 1000uL",
            "tiprack_50uL": "Tips 50uL",
            "workup_big": "Workup",
            "workup_small": "Workup",
            "trash": "Trash",
            "clean_up": "Clean up",
            "caps": "Reaction caps",
            "not_used": "Not_used",
            "plate_2mL": "GC LC"
        }
        assignment = assignment_dict[plate_type]
        slot = self.slots["slot"]
        chem_robot.deck.deck_config[slot] = {
            "plate": plate_name, "assignment": assignment}
        chem_robot.deck.save_deck_config(chem_robot.deck.deck_config)
        self.t.destroy()

    def cancel(self):
        self.t.destroy()


# This is the main entry of program
if __name__ == "__main__":
    logging.basicConfig(filename='myapp.log',
                        format='%(asctime)s %(message)s', level=logging.INFO)
    logging.info('Start...')

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
                    #background="dark green",
                    font=('Helvetica', 12, 'italic'),
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
    logging.info('Finished\n')

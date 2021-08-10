# coding=utf-8
# The robot module is the only entrance for hardware control

import time
import logging
import json
from pathlib import Path
from tkinter.constants import FALSE

from chem_robox.robot.drivers.xy_platform import xy_platform
from chem_robox.robot.drivers.z_platform import z_platform
from chem_robox.robot.drivers.rs485.gripper import gripper
from chem_robox.robot.drivers import rs485_connection
from chem_robox.robot.drivers.pipette import pipette_foreach
from chem_robox.robot.drivers.serial_connection import get_port_by_VID, get_port_by_VID_list, get_port_by_serial_no
from chem_robox.deck import deck

# Defined in parameters.py; CAPPER = 'Z1', TABLET = 'Z2', LOQUID = 'Z3'
from chem_robox.parameters import CAPPER, LIQUID, TABLET, GRIPPER_ID
# import tkinter as tk
from chem_robox.tools import custom_widgets, helper

# Gripper hold distance to the cap
HOLD_DISTANCE = 10
Z_NORMAL_SPEED = 3000 

class Robot(object):
    def __init__(
        self,
        xy_platform_port="",
        z_platform_port="",
        pipette_port="",
        gripper_port=""
    ):
        self.robot_config_file = Path("chem_robox/config/robot_config.json")
        self.xy_platform_port = xy_platform_port
        self.z_platform_port = z_platform_port
        self.pipette_port = pipette_port
        self.gripper_port = gripper_port
        self.ready = False
        self.stop_flag = False
        self.is_connected = False
        self.load_robot_config()
        self.deck = deck.Deck(self.robot_config)

    def load_robot_config(self):
        with open(self.robot_config_file) as config:
            self.robot_config = json.load(config)

    def get_usb_ports(self):
        # find usb port names
        # usb_sn_xy_platform = self.robot_config["usb_serial_no"]["xy_platform"]
        # usb_sn_z_platform = self.robot_config["usb_serial_no"]["z_platform"]
        # usb_sn_pipette = self.robot_config["usb_serial_no"]["pipette"]
        # usb_sn_gripper = self.robot_config["usb_serial_no"]["gripper"]

        # self.gripper_port = get_port_by_serial_no(usb_sn_gripper)
        # self.pipette_port = get_port_by_serial_no(usb_sn_pipette)
        # self.xy_platform_port = get_port_by_serial_no(usb_sn_xy_platform)
        # self.z_platform_port = get_port_by_serial_no(usb_sn_z_platform)

        usb_vid_xy_platform = self.robot_config["usb_serial_VID"]["xy_platform"]
        self.xy_platform_port = get_port_by_VID_list(usb_vid_xy_platform)

        usb_vid_z_platform = self.robot_config["usb_serial_VID"]["z_platform"]
        self.z_platform_port = get_port_by_VID_list(usb_vid_z_platform)

        usb_vid_pipette = self.robot_config["usb_serial_VID"]["pipette"]
        self.pipette_port = get_port_by_VID_list(usb_vid_pipette)

        usb_vid_gripper = self.robot_config["usb_serial_VID"]["gripper"]
        self.gripper_port = get_port_by_VID_list(usb_vid_gripper)

        usb_info = f"xy_port= {self.xy_platform_port}, z_port= {self.z_platform_port}, gripper_port= {self.gripper_port}, pipette_port= {self.pipette_port}"
        print(usb_info)
        logging.info("Com ports: " + usb_info)

    def connect(self):
        self.get_usb_ports()
        self.xy_platform = xy_platform.XY_platform(
            port=self.xy_platform_port,
            head_offsets=self.deck.head_offsets, firmware="Marlin"
        )
        self.xy_platform.connect()
        self.z_platform = z_platform.Z_platform(
            port=self.z_platform_port, head_offsets=self.deck.head_offsets)
        self.z_platform.connect()
        connection_485 = rs485_connection.RS485(
            port=self.gripper_port, baudrate=115200)
        self.gripper = gripper.Gripper(
            modbus_connection=connection_485, unit=GRIPPER_ID)
        self.pipette = pipette_foreach.Pipette(pipette_port=self.pipette_port)
        self.pipette.connect()

    def update(self):
        '''update head_offsets'''
        self.deck.update_head_offsets()
        self.xy_platform.update(
            head_offsets=self.deck.head_offsets)
        self.z_platform.update(head_offsets=self.deck.head_offsets)

    def home_all_z(self):
        '''home Z1, Z2 and Z3 together'''
        print("Start to home Z-Capper...")
        self.z_platform.home(head=CAPPER)
        print("Start to home Z-Tablet...")
        self.z_platform.home(head=TABLET)
        print("Start to home Z-Liquid...")
        self.z_platform.home(head=LIQUID)
        self.back_to_safe_position_all()

    def home_all(self):
        self.home_all_z()
        self.xy_platform.home('xy')
        self.pipette.initialization()
        self.gripper.initialization()
        self.gripper.rotate_to(360+90)
        self.ready = True

    def home_xy(self):
        self.xy_platform.home('xy')

    def go_home(self):
        self.back_to_safe_position_all()
        home_position = ("A3", "A1")
        self.move_to(head=TABLET, vial=home_position, use_allow_list=FALSE)

    def clean_up_after_stop(self):
        if self.ready:
            self.go_home()
            self.pipette.initialization()
            self.gripper.initialization()
        else:
            print("Robot not ready, going home failed")

    def get_axe_position(self, axe="x"):
        # axe = "x" "y" "z1", "z2", "z3"
        axe = axe.lower()  # conver to lower case, so both "Z1" or "z1" are accepatble
        if axe == "x" or axe == "y":
            position = self.xy_platform.get_position(axe)
        elif axe == "z1" or axe == "z2" or axe == "z3":
            position = self.z_platform.get_position(head=axe.upper())
        else:
            position = -1
            print("unknown axe name.")
        return position

    def vial(self, plate="A1", vial="A1"):
        return self.deck.vial(plate, vial)

    def set_stop_flag(self, stop=True):
        ''' if not ready, run in simulation mode without stopping XY and Z axies'''
        if self.ready:
            self.stop_flag = stop
            # self.xy_platform.stop_flag = stop
            # self.z_platform.stop_flag = stop
        else:
            self.stop_flag = stop

    def back_to_safe_position(self, head):
        if head == CAPPER:
            safe_position = 85
        if head == LIQUID:
            safe_position = 5
        if head == TABLET:
            safe_position = 35
        self.z_platform.move_to_abs(head=head, z=safe_position)

    def back_to_safe_position_all(self):
        self.back_to_safe_position(head=CAPPER)
        self.back_to_safe_position(head=LIQUID)
        self.back_to_safe_position(head=TABLET)

    def move_to(self, head=CAPPER, vial=(), use_allow_list=True):
        # vial is a turple for vial location, e.g., ('A1', 'C2')
        # the first ('A1') is for plate, the second ('C2') is for vial location
        # ("Reagent", "Reactor", "Workup", "Tips 1000uL", "Tips 50uL", "Trash", "Clean up", "Reaction caps", "GC LC")
        assignment = self.deck.get_assignment_of_slot(vial[0])
        allowed_list = {CAPPER: ["Reactor", "Reagent", "Reaction caps", "Workup"],
                        LIQUID: ["Workup", "Reactor", "Tips 1000uL", "Tips 50uL", "Reagent", "GC LC", "Trash"],
                        TABLET: ["Reagent", "Reactor", "Clean up"]
                        }
        if assignment not in allowed_list[head] and use_allow_list == True:
            print(f"{head} should not move to {assignment}")
            return assignment
        my_vial = self.vial(vial[0], vial[1])
        self.back_to_safe_position_all()
        response = self.xy_platform.move_to(head=head, vial=my_vial)
        return response

    def move_to_top_of_vial(self, head=CAPPER, vial=(), z=0):
        '''Move Z head to the top of the vial'''
        # e.g., use z = -7 (mm) to move the head to a lower position for dipensing and hold the cap
        if self.ready:
            my_vial = self.vial(vial[0], vial[1])
            vial_height = my_vial["height"]
            response = self.z_platform.move_to(head=head, z=vial_height + z)
            return response
        else:
            print("Robot not ready")

    def move_to_bottom_of_vial(self, head=CAPPER, vial=(), z=0):
        '''Move Z head to the bottom of the vial'''
        # e.g., use z = -7 (mm) to move the head to a lower position for dipensing and hold the cap
        if self.ready:
            my_vial = self.vial(vial[0], vial[1])
            vial_depth = my_vial["depth"]
            vial_height = my_vial["height"]
            response = self.z_platform.move_to(
                head=head, z=vial_height-vial_depth + z)
            return response
        else:
            print("Robot not ready")

    # high level functions

    def lock_vial_before_decap(self, vial_type="plate_5mL"):
        ''' make sure a 5 mL vial in lock position by rotate the vial and push down a small distance at the same time'''
        if self.ready:
            ROTATION = 80
            DOWN = -2
            self.gripper.rotate(ROTATION)
            self.z_platform.move(head=CAPPER, z=DOWN)
            time.sleep(0.5)
        else:
            print("Robot not ready")

    def decap(self, vial=()):
        if not self.ready:
            print("Robot not ready")
            return "not ready"
        if self.gripper.is_gripper_holding():
            print("can open cap because a cap is already holded")
            return "cap hold"
        if self.check_stop_status() == "stop":
            return "stop"
        my_vial = self.vial(vial[0], vial[1])
        vial_type = my_vial["type"]
        self.z_platform.set_max_speed(
            head=CAPPER, speed=Z_NORMAL_SPEED)  # normal Max speed = 3000
  
        if vial_type == "reactor_27p":
            # hold = -11
            rotation_speed = 80
            rotation_force = 90
            ratio = 6.0
            Z_speed = int(rotation_speed*ratio)
            rotation_angle = 2000
            gripper_openning_percent = 75  # 90%
            up_distance = 7
            gripper_closing_percent = 20
        elif vial_type == "plate_5mL":
            # hold = -12
            rotation_speed = 40
            rotation_force = 90
            ratio = 7.0
            Z_speed = int(rotation_speed*ratio)
            rotation_angle = 1100
            gripper_openning_percent = 50
            up_distance = 10
            gripper_closing_percent = 10

        elif vial_type == "reactor_12p":
            # hold = -7
            rotation_speed = 70
            rotation_force = 90
            ratio = 5.0
            Z_speed = int(rotation_speed*ratio)
            rotation_angle = 1400
            gripper_openning_percent = 70
            up_distance = 6
            gripper_closing_percent = 20

        # 8-mL vial
        elif vial_type in ["reactor_circle_8mL_20p", "reactor_circle_8mL_10p", "reactor_square_8mL_20p", "workup_8mL_20p"]:
            # hold = -7
            rotation_speed = 99
            rotation_force = 90
            ratio = 5.0
            Z_speed = int(rotation_speed*ratio)
            rotation_angle = 1500
            gripper_openning_percent = 75
            gripper_closing_percent = 20
            up_distance = 6

        elif vial_type == "plate_50mL" or vial_type == "plate_10mL":
            hold = -6
            rotation_speed = 70
            rotation_force = 90
            ratio = 5.0
            Z_speed = int(rotation_speed*ratio)
            rotation_angle = 1200
            gripper_openning_percent = 100
            gripper_closing_percent = 20
            up_distance = 10
        else:
            print("unknow cap type!")
            return "unknow cap"

        self.gripper.set_rotation_force(rotation_force)
        self.move_to(head=CAPPER, vial=vial)
        self.gripper.gripper_open(gripper_openning_percent)
        self.move_to_top_of_vial(head=CAPPER, vial=vial, z=HOLD_DISTANCE*-1)
        self.gripper.gripper_close(gripper_closing_percent)
        if vial_type == "plate_5mL":
            self.lock_vial_before_decap()
            self.gripper.gripper_close(gripper_openning_percent)
            self.move_to_top_of_vial(head=CAPPER, vial=vial, z=hold)
            self.gripper.gripper_close(gripper_closing_percent)
            self.z_platform.move(head=CAPPER, z=-1)
        else:
            self.z_platform.move(head=CAPPER, z=-1)
        self.gripper.set_rotation_speed(rotation_speed)
        self.gripper.rotate(rotation_angle)
        self.z_platform.set_max_speed(head=CAPPER, speed=Z_speed)
        self.z_platform.move(head=CAPPER, z=up_distance)
        self.z_platform.set_max_speed(
            head=CAPPER, speed=Z_NORMAL_SPEED)  # normal Max speed = 3000
        self.back_to_safe_position(head=CAPPER)
        if self.gripper.is_gripper_holding():
            return "finish"
        else:
            print("error: no cap holded!")
            return "error"

    def recap(self, vial=()):
        if not self.ready:
            print("not ready")
            return "not ready"
        if self.gripper.is_gripper_holding():
            my_vial = self.vial(vial[0], vial[1])
            vial_type = my_vial["type"]
            self.z_platform.set_max_speed(
                head=CAPPER, speed=4000)  # normal Max speed = 4000
            time.sleep(0.1)
            if vial_type == "reactor_27p":
                adjustment = -3  # cap hold distance
                rotation_speed = 80
                rotation_force = 40
                ratio = 6.0
                Z_speed = int(rotation_speed*ratio)
                cap_down = -8
                rotation_angle = -2000
                gripper_openning_percent = 75

            if vial_type == "reactor_12p":
                adjustment = -3  # cap hold distance
                rotation_speed = 80
                rotation_force = 40
                ratio = 6.0
                Z_speed = int(rotation_speed*ratio)
                cap_down = -8
                rotation_angle = -2000
                gripper_openning_percent = 70

            if vial_type in ["reactor_circle_8mL_20p", "reactor_circle_8mL_10p", "reactor_square_8mL_20p", "workup_8mL_20p"]:
                adjustment = -3  # cap hold distance
                rotation_speed = 60
                rotation_force = 30
                ratio = 8
                Z_speed = int(rotation_speed*ratio)
                cap_down = -4
                rotation_angle = -1500
                gripper_openning_percent = 70

            if vial_type == "plate_5mL":
                adjustment = -5  # cap hold distance
                rotation_speed = 30
                rotation_force = 30
                ratio = 18
                Z_speed = int(rotation_speed*ratio)
                cap_down = -8
                rotation_angle = -1100
                gripper_openning_percent = 40

            if vial_type == "reactor_12p_8mL":
                adjustment = -4  # cap hold distance
                rotation_speed = 70
                rotation_force = 30
                ratio = 8.0
                Z_speed = int(rotation_speed*ratio)
                cap_down = -5.5
                rotation_angle = -1400
                gripper_openning_percent = 70

            if vial_type == "plate_50mL" or vial_type == "plate_10mL":
                adjustment = -3  # cap hold distance
                rotation_speed = 70
                rotation_force = 30
                ratio = 3
                Z_speed = int(rotation_speed*ratio)
                rotation_angle = -1200
                cap_down = -5.5
                gripper_openning_percent = 100

            self.move_to(head=CAPPER, vial=vial)
            self.move_to_top_of_vial(
                head=CAPPER, vial=vial, z=adjustment)
            self.gripper.set_rotation_force(rotation_force)
            self.gripper.set_rotation_speed(rotation_speed)
            self.gripper.rotate(rotation_angle)
            self.z_platform.set_max_speed(
                head=CAPPER, speed=Z_speed)  # normal Max speed = 4000
            self.z_platform.move(head=CAPPER, z=cap_down)
            time.sleep(0.3)
            self.gripper.gripper_open(gripper_openning_percent)
            self.z_platform.set_max_speed(
                head=CAPPER, speed=4000)  # normal Max speed = 4000
            self.back_to_safe_position(CAPPER)
            return "finish"
        else:
            print('No cap!')
            return "no cap"

    def pickup_cap(self, vial=()):
        if not self.ready:
            print("not ready")
            return "not ready"
        if self.gripper.is_gripper_holding():
            print("Cap already holded")
            return "cap hold"
        gripper_openning_percent = 75
        hold = -10
        rotation_angle = 1500
        self.move_to(head=CAPPER, vial=vial)
        self.gripper.gripper_open(gripper_openning_percent)
        self.move_to_top_of_vial(head=CAPPER, vial=vial, z=hold)
        self.gripper.gripper_close(10)
        self.back_to_safe_position(head=CAPPER)
        self.gripper.rotate(rotation_angle)
        if self.gripper.is_gripper_holding():
            return "finish"
        else:
            return "error"

    def return_cap(self, vial=()):
        if not self.ready:
            return
        if not self.gripper.is_gripper_holding():
            print("No cap is holded")
            return
        gripper_openning_percent = 80
        rotation_angle = -1500
        self.move_to(head=CAPPER, vial=vial)
        down = -9
        self.move_to_top_of_vial(head=CAPPER, vial=vial, z=down)
        self.gripper.gripper_open(gripper_openning_percent)
        self.gripper.rotate(rotation_angle)
        self.back_to_safe_position(head=CAPPER)
        if self.gripper.is_gripper_holding():
            return "error"
        else:
            return "finish"

    # tablet functions

    def pickup_tablet(self, vial):
        if not self.ready:
            print("Robot not ready!")
            return "not ready"
        self.move_to(head=TABLET, vial=vial)
        # self.move_to_top_of_vial(head=TABLET, vial=vial)
        DEPTH = (-84-82+5)*-1
        self.z_platform.pickup_tablet(z=DEPTH)
        self.back_to_safe_position(head=TABLET)
        return "finish"

    def drop_tablet(self, vial):
        if not self.ready:
            print("Robot not ready!")
            return
        self.move_to(head=TABLET, vial=vial)
        self.move_to_top_of_vial(head=TABLET, vial=vial)
        self.z_platform.drop_tablet()
        self.back_to_safe_position(head=TABLET)
        return "finish"

    def transfer_tablet(self, vial_from=None, vial_to=None,
                        number_of_tablet=1):
        if not self.ready:
            return
        for _ in range(number_of_tablet):
            self.pickup_tablet(vial_from)
            self.drop_tablet(vial_to)

    def clean_up_needle(self, vial):
        if not self.ready:
            return "not ready"
        self.move_to(head=TABLET, vial=vial)
        # self.move_to_top_of_vial(head=TABLET, vial=vial)
        # self.z_platform.pickup_tablet(z=-40)
        self.z_platform.move_to(head=TABLET, z=155)
        self.back_to_safe_position(head=TABLET)
        return "finish"

    # liquid functions
    def pickup_tip(self, vial, tip_type="tips_1000uL"):
        if not self.ready:
            return
        if self.pipette.is_tip_attached():
            msg = "tip already attached"
            print(msg)
            return msg
        self.pipette.send_pickup_tip_cmd()
        self.move_to(head=LIQUID, vial=vial)
        tip_position = self.deck.calibration[tip_type][2]
        self.z_platform.move_to_abs(head=LIQUID, z=tip_position)
        self.back_to_safe_position(head=LIQUID)
        if self.pipette.is_tip_attached():
            print("pickup tip successfully")
            msg = "finish"
            return msg
        else:
            msg = "pickup tip failed"
            print(msg)
            return msg

    def aspirate(self, vial=(), volume=0, tip_type="tips_1000uL", tip_extraction_adjustment=0):
        '''vial=("A1", "B1"), volume= xx uL'''
        # the function does move to target location
        if not self.ready:
            return "not ready"

        # used to blow out all liquids
        blow_out = 20
        self.pipette.aspirate(volume=blow_out)
        tip_length_adjustment = -1 * \
            self.robot_config["tip_length_adjustment"][tip_type]
        print("tip_length_adjustment", tip_length_adjustment)
        self.move_to_bottom_of_vial(
            head=LIQUID, vial=vial, z=tip_length_adjustment + tip_extraction_adjustment)
        self.pipette.aspirate(volume)
        return "finish"

    def dispense(self, vial=(), volume=0, tip_type="tips_1000uL", z=-5):
        '''dispense all liquid in the tip, vial=(), volume= xx uL'''
        # self.pipette.enable_anti_dropping()
        if not self.ready:
            return
        # self.move_to(head=LIQUID, vial=vial)
        tip_length_adjustment = -1 * \
            self.robot_config["tip_length_adjustment"][tip_type] + z
        self.move_to_top_of_vial(
            head=LIQUID, vial=vial, z=tip_length_adjustment)
        self.pipette.dispense(volume)
        return "finish"

    def drop_tip(self, vial=()):
        if not self.ready:
            return
        self.move_to(head=LIQUID, vial=vial)
        self.move_to_top_of_vial(head=LIQUID, vial=vial, z=-60)
        self.pipette.send_drop_tip_cmd()
        self.back_to_safe_position(head=LIQUID)

    def preparation_for_volatile(self, vial=(), tip_type="tips_1000uL", counter=2, h=0):
        # h is the height adjuctment
        if tip_type == "tips_1000uL":
            VOL = 600
        else:
            VOL = 30
        for i in range(counter):
            if self.check_stop_status() == "stop":
                return "stop"
            self.move_to_bottom_of_vial(head=LIQUID, vial=vial, z=h)
            if self.check_stop_status() == "stop":
                return "stop"
            self.pipette.aspirate(VOL)
            if self.check_stop_status() == "stop":
                return "stop"
            self.move_to_top_of_vial(head=LIQUID, vial=vial, z=-10)
            if self.check_stop_status() == "stop":
                return "stop"
            self.pipette.dispense()

    def transfer_liquid(self, vial_from=(), vial_to=(),
                        tip=None, trash=(), volume=0, is_volatile="no", tip_type="tips_1000uL", is_extraction=False, tip_extraction_adjustment=0, z=-10):
        '''vial_from=("A1", "B1"), volume=mL, when tip = None, no tip will be used, z is used for adjustment of height of tip'''
        if not self.ready:
            return
        MAX = 1000
        SLOW_SPEED = 18
        NORMAL_SPEED = 11
        liquid_volume = volume*1000  # convert to uL
        cycles = int(int(liquid_volume)/MAX)
        residue = int(liquid_volume) % MAX
        volume_list = []
        for _ in range(cycles):
            volume_list.append(MAX)
        if residue > 0:
            volume_list.append(residue)
        print(volume_list)

        if tip != None:
            if self.check_stop_status() == "stop":
                return "stop"
            self.pickup_tip(vial=tip, tip_type=tip_type)

        self.move_to(head=LIQUID, vial=vial_from)
        if is_volatile == "yes":
            self.preparation_for_volatile(vial=vial_from)
        if is_extraction:
            self.preparation_for_volatile(vial=vial_from, h=15)

        is_first = True
        for vol in volume_list:
            if self.check_stop_status() == "stop":
                return "stop"
            if is_extraction:
                self.pipette.set_speed(SLOW_SPEED)
            if not (is_volatile and is_first):
                self.move_to(head=LIQUID, vial=vial_from)
            self.aspirate(vial=vial_from, volume=vol, tip_type=tip_type,
                          tip_extraction_adjustment=tip_extraction_adjustment)
            if self.check_stop_status() == "stop":
                return "stop"
            if tip_type == "tips_1000uL":
                wait_height = -55
            else:
                wait_height = -35
            tip_length_adjustment = -1 * \
                self.robot_config["tip_length_adjustment"][tip_type]
            self.move_to_top_of_vial(
                head=LIQUID, vial=vial_from, z=wait_height+tip_length_adjustment)
            time.sleep(1)
            if self.check_stop_status() == "stop":
                return "stop"
            if tip_type == "tips_1000uL":
                transport_air_volume = 20
            else:
                transport_air_volume = 0
            if transport_air_volume > 0:
                self.move_to_top_of_vial(head=LIQUID, vial=vial_from)
                self.pipette.set_transport_air_volume(transport_air_volume)
            if self.check_stop_status() == "stop":
                return "stop"
            if is_extraction:
                self.pipette.set_speed(NORMAL_SPEED)
            self.move_to(head=LIQUID, vial=vial_to)
            self.dispense(vial=vial_to, tip_type=tip_type)
            is_first = False

        if tip != None:
            if self.check_stop_status() == "stop":
                return "stop"
            self.drop_tip(vial=trash)

    def check_stop_status(self):
        if self.stop_flag:
            res = custom_widgets.stop_or_resume()
            if res == "stop":
                self.clean_up_after_stop()
                return "stop"
            else:
                self.set_stop_flag(False)
                return "resume"


# misc funcitons
    # use mosfets to control the lights


    def green_light(self, state='on'):
        GREEN_MOSFET = 2
        if state.lower() == 'on':
            self.xy_platform.mosfet_engage(GREEN_MOSFET)
        else:
            self.xy_platform.mosfet_disengage(GREEN_MOSFET)

    def red_light(self, state='on'):
        RED_MOSFET = 3
        if state.lower() == 'on':
            self.xy_platform.mosfet_engage(RED_MOSFET)
        else:
            self.xy_platform.mosfet_disengage(RED_MOSFET)

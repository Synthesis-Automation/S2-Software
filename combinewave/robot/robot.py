# coding=utf-8
# The robot module is the only entrance for hardware control

import time
import logging

from combinewave.robot.drivers.xy_platform import xy_platform
from combinewave.robot.drivers.z_platform import z_platform
from combinewave.robot.drivers.rs485.gripper import gripper
from combinewave.robot.drivers import rs485_connection
from combinewave.robot.drivers import pipette_foreach
from combinewave.robot.drivers.serial_connection import get_port_by_VID
from combinewave.deck import deck

# Defined in parameters.py; CAPPER = 'Z1', TABLET = 'Z2', LOQUID = 'Z3'
from combinewave.parameters import CAPPER, LIQUID, TABLET, GRIPPER_ID
import tkinter as tk


class Robot(object):
    def __init__(
        self,
        xy_platform_port="",
        z_platform_port="",
        pipette_port="",
        modbus_port=""
    ):
        self.xy_platform_port = xy_platform_port
        self.z_platform_port = z_platform_port
        self.pipette_port = pipette_port
        self.modbus_port = modbus_port
        self.ready = False
        self.stop_flag = False
        self.deck = deck.Deck()
        self.is_connected = False

    def connect(self):
        # find usb ports
        vid_xy_platform = 0x1D50  # smoothie
        vid_z_platform = 0x1A86  # CH340
        vid_pipette = 0x0403  # FT232
        vid_modbus = 0x10C4  # CP210x, PID 0xEA60, DTECH/UGreen

        self.xy_platform_port = get_port_by_VID(vid_xy_platform)
        self.z_platform_port = get_port_by_VID(vid_z_platform)
        self.modbus_port = get_port_by_VID(vid_modbus)
        self.pipette_port = get_port_by_VID(vid_pipette)
        usb_info = f"xy_port= {self.xy_platform_port}, z_port= {self.z_platform_port}, modbus_port= {self.modbus_port}, pipette_port= {self.pipette_port}"
        logging.info(usb_info)
        self.xy_platform = xy_platform.XY_platform(
            port=self.xy_platform_port,
            head_offsets=self.deck.head_offsets,
            calibration=self.deck.calibration
        )
        self.xy_platform.connect()
        self.z_platform = z_platform.Z_platform(
            port=self.z_platform_port, head_offsets=self.deck.head_offsets)
        self.z_platform.connect()
        connection_485 = rs485_connection.RS485(
            port=self.modbus_port, baudrate=115200)
        self.gripper = gripper.Gripper(
            modbus_connection=connection_485, unit=GRIPPER_ID)
        self.pipette = pipette_foreach.Pipette(pipette_port=self.pipette_port)
        self.pipette.connect()

    def update(self):
        '''update calibration and head_offsets'''
        self.deck.update_head_offsets()
        self.xy_platform.update(
            head_offsets=self.deck.head_offsets, calibration=self.deck.calibration)
        self.z_platform.update(head_offsets=self.deck.head_offsets)

    def home_all(self):
        # if self.is_simulation:
        #     return 'simulation'
        self.home_all_z()
        self.xy_platform.home('xy')
        self.pipette.initialization()
        self.gripper.initialization()
        self.gripper.rotate_to(360+90)
        self.gripper.gripper_close(5)
        self.ready = True

    def home_all_z(self):
        '''home Z1, Z2 and Z3 together'''
        self.z_platform.home(head=CAPPER)
        self.z_platform.home(head=TABLET)
        self.z_platform.home(head=LIQUID)
        self.back_to_safe_position_all()

    def home_xy(self):
        self.xy_platform.home('xy')

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
            safe_position = 2
        if head == LIQUID:
            safe_position = 2
        if head == TABLET:
            safe_position = 2
        self.z_platform.move_to_abs(head=head, z=safe_position)

    def back_to_safe_position_all(self):
        self.back_to_safe_position(head=CAPPER)
        self.back_to_safe_position(head=LIQUID)
        self.back_to_safe_position(head=TABLET)

    def move_to(self, head=CAPPER, vial=()):
        # vial is a turple for vial location, e.g., ('A1', 'C2')
        # the first ('A1') is for plate, the second ('C2') is for vial location
        # ("Reagent", "Reactor", "Workup", "Tips 1000uL", "Tips 50uL", "Trash", "Clean up", "Reaction caps", "GC LC")
        assignment = self.deck.get_assignment_of_slot(vial[0])
        allowed_list = {CAPPER: ["Reactor", "Reagent", "Reaction caps"],
                        LIQUID: ["Workup", "Reactor", "Tips 1000uL", "Reagent", "GC LC", "Trash"],
                        TABLET: ["Reagent", "Reactor", "Clean up"]
                        }
        if assignment not in allowed_list[head]:
            print(f"{head} can not move to {assignment}")
            return assignment
        my_vial = self.vial(vial[0], vial[1])
        self.back_to_safe_position_all()
        response = self.xy_platform.move_to(head=head, vial=my_vial)
        return response

    def move_to_top_of_vial(self, head=CAPPER, vial=(), z=0):
        '''Move Z head to the top of the vial'''
        # e.g., use z = -7 (mm) to move the head to a lower position for dipense and hold the cap
        my_vial = self.vial(vial[0], vial[1])
        vial_height = my_vial["height"]
        response = self.z_platform.move_to(head=head, z=vial_height + z)
        return response

    def move_to_bottom_of_vial(self, head=CAPPER, vial=()):
        '''Move Z head to the bottom of the vial'''
        my_vial = self.vial(vial[0], vial[1])
        vial_depth = my_vial["depth"]
        vial_height = my_vial["height"]
        response = self.z_platform.move_to(head=head, z=vial_height-vial_depth)
        return response

    # high level functions
    def decap(self, vial=()):
        if self.gripper.is_gripper_holding():
            print("can open cap because a cap is already holded")
            return False
        if self.check_stop_status() == "stop":
            return False
        my_vial = self.vial(vial[0], vial[1])
        vial_type = my_vial["type"]
        self.gripper.set_gripper_force(100)
        hold = -8
        self.z_platform.set_max_speed(
            head=CAPPER, speed=4000)  # normal Max speed = 4000
        if vial_type == "plate_15mL":
            rotation_speed = 80
            rotation_force = 90
            ratio = 6.0
            Z_speed = int(rotation_speed*ratio)
            rotation_angle = 1400
            gripper_openning_percent = 70  # 90%
            up_distance = 7
            gripper_closing_percent = 20
        elif vial_type == "plate_5mL":
            rotation_speed = 40
            rotation_force = 90
            ratio = 9.0
            Z_speed = int(rotation_speed*ratio)
            rotation_angle = 900
            gripper_openning_percent = 50
            up_distance = rotation_angle/100
            gripper_closing_percent = 10
        elif vial_type == "plate_8mL":
            rotation_speed = 70
            rotation_force = 90
            ratio = 6.0
            Z_speed = int(rotation_speed*ratio)
            rotation_angle = 1400
            gripper_openning_percent = 70
            up_distance = 7
            gripper_closing_percent = 20
        elif vial_type == "plate_40mL":
            hold = -12
            rotation_speed = 40
            rotation_force = 90
            ratio = 10.0
            Z_speed = int(rotation_speed*ratio)
            rotation_angle = 1000
            gripper_openning_percent = 100  # percent%
            gripper_closing_percent = 20
            up_distance = rotation_angle/100
        else:
            print("unknow cap type!")
            return False
        self.gripper.set_rotation_force(rotation_force)
        self.move_to(head=CAPPER, vial=vial)
        self.gripper.gripper_open(gripper_openning_percent)
        self.move_to_top_of_vial(head=CAPPER, vial=vial, z=hold)
        self.gripper.gripper_close(gripper_closing_percent)
        self.gripper.set_rotation_speed(rotation_speed)
        self.gripper.rotate(rotation_angle)
        self.z_platform.set_max_speed(head=CAPPER, speed=Z_speed)
        self.z_platform.move(head=CAPPER, z=up_distance)
        self.z_platform.set_max_speed(
            head=CAPPER, speed=3000)  # normal Max speed = 3000
        self.back_to_safe_position(head=CAPPER)
        r = self.gripper.get_rotation_status()
        if self.gripper.is_gripper_holding():
            return True
        else:
            return False

    def recap(self, vial=()):
        if self.gripper.is_gripper_holding():
            my_vial = self.vial(vial[0], vial[1])
            vial_type = my_vial["type"]
            self.z_platform.set_max_speed(
                head=CAPPER, speed=4000)  # normal Max speed = 4000
            time.sleep(0.1)
            hold = -8  # cap hold distance
            if vial_type == "plate_15mL":
                rotation_speed = 80
                rotation_force = 60
                ratio = 9.0
                Z_speed = int(rotation_speed*ratio)
                up_distance = 6
                rotation_angle = -1400
                gripper_openning_percent = 70
            if vial_type == "plate_5mL":
                rotation_speed = 30
                rotation_force = 30
                ratio = 18
                Z_speed = int(rotation_speed*ratio)
                up_distance = 8
                rotation_angle = -900
                gripper_openning_percent = 40
            if vial_type == "plate_8mL":
                rotation_speed = 70
                rotation_force = 30
                ratio = 8.0
                Z_speed = int(rotation_speed*ratio)
                up_distance = 6
                rotation_angle = -1400
                gripper_openning_percent = 70
            if vial_type == "plate_40mL":
                hold = -11
                rotation_speed = 70
                rotation_force = 30
                ratio = 20
                Z_speed = int(rotation_speed*ratio)
                rotation_angle = -1000
                up_distance = 5.5
                gripper_openning_percent = 100

            self.move_to(head=CAPPER, vial=vial)
            self.move_to_top_of_vial(
                head=CAPPER, vial=vial, z=hold+up_distance)
            self.gripper.set_rotation_force(rotation_force)
            self.gripper.set_rotation_speed(rotation_speed)
            self.gripper.rotate(rotation_angle)
            self.z_platform.set_max_speed(
                head=CAPPER, speed=Z_speed)  # normal Max speed = 4000
            self.z_platform.move(head=CAPPER, z=-1*up_distance)
            self.gripper.gripper_open(gripper_openning_percent)
            self.z_platform.set_max_speed(
                head=CAPPER, speed=4000)  # normal Max speed = 4000
            self.back_to_safe_position(CAPPER)
        else:
            print('No cap!')

    def pickup_cap(self, vial=()):
        if self.gripper.is_gripper_holding():
            print("Cap already holded")
            return
        gripper_openning_percent = 100
        hold = -9
        rotation_angle = 1400
        self.move_to(head=CAPPER, vial=vial)
        self.gripper.gripper_open(gripper_openning_percent)
        self.move_to_top_of_vial(head=CAPPER, vial=vial, z=hold)
        self.gripper.gripper_close(10)
        self.back_to_safe_position(head=CAPPER)
        self.gripper.rotate(rotation_angle)
        if self.gripper.is_gripper_holding():
            return True
        else:
            return False

    def recap_by_press(self, vial=()):
        self.move_to(head=CAPPER, vial=vial)
        # self.gripper.set_gripper_force(50)
        #self.z_platform.move(head = CAPPER,z = 4)
        self.move_to_top_of_vial(head=TABLET, vial=vial, z=5)
        self.gripper.gripper_open(40)
        self.back_to_safe_position(head=CAPPER)

    # tablet functions

    def pickup_tablet(self, vial):
        self.move_to(head=TABLET, vial=vial)
        self.move_to_top_of_vial(head=TABLET, vial=vial)
        DEPTH = -80
        self.z_platform.pickup_tablet(z=DEPTH)
        self.back_to_safe_position(head=TABLET)

    def drop_tablet(self, vial):
        self.move_to(head=TABLET, vial=vial)
        self.move_to_top_of_vial(head=TABLET, vial=vial)
        self.z_platform.drop_tablet()
        self.back_to_safe_position(head=TABLET)

    def transfer_tablet(self, vial_from=None, vial_to=None,
                        number_of_tablet=1):
        for _ in range(number_of_tablet):
            self.pickup_tablet(vial_from)
            self.drop_tablet(vial_to)

    def clean_up_needle(self, vial):
        self.move_to(head=TABLET, vial=vial)
        self.move_to_top_of_vial(head=TABLET, vial=vial)
        self.z_platform.pickup_tablet(z=-40)
        self.back_to_safe_position(head=TABLET)

    # liquid functions
    def pickup_tip(self, vial, tip="Tips_1000uL"):
        if self.pipette.is_tip_attached():
            msg = "tip already attached"
            print(msg)
            return msg
        self.pipette.send_pickup_tip_cmd()
        self.move_to(head=LIQUID, vial=vial)
        tip_position = self.deck.calibration["Tips_1000uL"][2]
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

    def aspirate(self, vial=(), volume=0):
        '''vial=("A1", "B1"), volume= xx uL'''
        self.move_to(head=LIQUID, vial=vial)
        self.move_to_bottom_of_vial(head=LIQUID, vial=vial)
        self.pipette.aspirate(volume)
        self.last_volume = volume
        # self.pipette.enable_anti_dropping()

    def dispense(self, vial=(), volume=0):
        '''vial=(), volume= xx'''
        # self.pipette.enable_anti_dropping()
        if volume == 0:  # make the defaut volume is the everything in the piptette
            liquid_volume = self.last_volume
        else:
            liquid_volume = volume
        self.move_to(head=LIQUID, vial=vial)
        self.move_to_top_of_vial(head=LIQUID, vial=vial, z=-5)
        self.pipette.dispense(liquid_volume)

    def drop_tip(self, vial=()):
        self.move_to(head=LIQUID, vial=vial)
        self.pipette.send_drop_tip_cmd()
        time.sleep(0.05)

    def transfer_liquid(self, vial_from=(), vial_to=(),
                        tip=None, trash=(), volume=0):
        '''vial_from=("A1", "B1"), volume=mL, when tip = None, no tip will be used'''
        MAX = 1000
        liquid_volume = volume*1000
        cycles = int(int(liquid_volume)/MAX)
        residue = int(liquid_volume) % MAX
        if tip != None:
            self.pickup_tip(vial=tip)
        for _ in range(cycles):
            self.aspirate(vial=vial_from, volume=MAX)
            # 10 mm lower from the top of the vial
            self.move_to_top_of_vial(head=LIQUID, vial=vial_from, z=-10)
            self.pipette.set_transport_air_volume(volume=20)
            self.dispense(vial=vial_to, volume=MAX)
        if residue != 0:
            self.aspirate(vial=vial_from, volume=residue)
            self.move_to_top_of_vial(head=LIQUID, vial=vial_from, z=-10)
            self.pipette.set_transport_air_volume(volume=20)
            self.dispense(vial=vial_to, volume=residue)
        if tip != None:
            self.drop_tip(vial=trash)

    def check_stop_status(self):
        if self.stop_flag:
            yes = tk.messagebox.askyesno(
                "Warning", "Are you sure want to stop?")
            if yes:
                return "stop"
            else:
                self.set_stop_flag(False)
                return "continue"

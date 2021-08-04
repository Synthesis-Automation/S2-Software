'''Z is relative the surface of deck'''

import sys
import time
from chem_robox.robot.drivers import serial_connection
from chem_robox import parameters
import logging
from chem_robox.parameters import CAPPER, LIQUID, TABLET

class Z_platform(object):
    def __init__(self, port="", head_offsets={}, calibration={}):
        self.port = port
        self.calibration = calibration
        self.head_offsets = head_offsets
        self.stop_flag = False
        self.pause_flag = False

    def connect(self):
        self.serial_connection = serial_connection.Connection(
            port=self.port, baudrate=115200)
        time.sleep(1)
        is_open = self.serial_connection.isOpen()
        if is_open:
            print("Z-platform connected")
        else:
            logging.info("Z-platform failed to connect")

    # following is capper functions
    def update(self, head_offsets={}, calibration={}):
        self.calibration = calibration
        self.head_offsets = head_offsets

    def home(self, head='Z1'):
        cmd = 'home_' + head + '$0'
        if self.stop_flag == False:
            self.serial_connection.send_command(cmd)
            self.serial_connection.wait_for_finish()

    def set_max_speed(self, head='Z1', speed=4000):
        cmd = 'set_max_speed_' + head + "$"+str(speed)
        if self.stop_flag == False:
            self.serial_connection.send_command(cmd)
            self.serial_connection.wait_for_finish()

    def get_position(self, head='Z1'):
        cmd = 'position_'+head+'$0'
        steps_per_mm = parameters.steps_per_mm_Z
        self.serial_connection.send_command(cmd)
        while True:
            msg = self.serial_connection.readline_string()
            if 'finish' in msg:
                position = int(''.join(filter(str.isdigit, msg)))/steps_per_mm
                return(position)
            elif 'error' in msg:
                print("error occurs, quit to system")
                return(False)

    def move_to(self, head='Z1', z=0):
        if self.stop_flag:
            self.home(head = head)
            return False
        new_z = self.head_offsets[head][2]-z
        cmd = 'move_to_'+head+'$' + str(int(new_z*parameters.steps_per_mm_Z))
        self.serial_connection.send_command(cmd)
        self.serial_connection.wait_for_finish()
        return True

    def move_to_abs(self, head='Z1', z=0):
        """this function use unfliped coordinates """
        if self.stop_flag:
            self.home(head = head)
            return False
        new_z = z
        cmd = 'move_to_'+head+'$' + str(int(new_z*parameters.steps_per_mm_Z))
        self.serial_connection.send_command(cmd)
        self.serial_connection.wait_for_finish()
        return True

    def move(self, head=CAPPER, z=0):
        if self.stop_flag:
            self.home(head = head)
            return False
        cmd = 'move_'+head+'$' + str(int(-1*z*parameters.steps_per_mm_Z))
        self.serial_connection.send_command(cmd)
        self.serial_connection.wait_for_finish()
        return True

    # following is tablet functions

    def pickup_tablet(self, z=100):
        # z is the how much mm the needle will go down to pick the tablet
        if self.stop_flag == False:
            move = z
            h = str(int(move*parameters.steps_per_mm_Z))  # h=32768 max
            cmd = 'pickup_tablet$' + h
            self.serial_connection.send_command(cmd)
            self.serial_connection.wait_for_finish()
        else:
            self.home(head = TABLET)
            return False


    def drop_tablet(self):  # this function only eject tablet and no Z movement
        if self.stop_flag == False:
            cmd = 'drop_tablet$0'
            self.serial_connection.send_command(cmd)
            self.serial_connection.wait_for_finish()
            return True
        else:
            self.home(head = TABLET)
            return False

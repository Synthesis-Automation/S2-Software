import sys
import time
import logging
from combinewave.robot.drivers import serial_connection


class Pipette(object):
    def __init__(self, pipette_port):
        self.pipette_port = pipette_port

    def connect(self):
        self.serial_connection = serial_connection.Connection(
            port=self.pipette_port, baudrate=38400)
        time.sleep(1)
        is_open = self.serial_connection.isOpen()
        if is_open:
            logging.info("E-pipette connected")
        else:
            logging.info("E-pipette failed to connect")

    def initialization(self):
        init_cmd = '/1ZR\r'
        self.serial_connection.write_string(init_cmd)
        time.sleep(0.05)
        self.serial_connection.wait_for_pipette(model="foreach")
        normal_mode = "/1N0R\r"
        # N0 mode and N1 mode
        self.serial_connection.write_string(normal_mode)
        self.serial_connection.wait_for_pipette(model="foreach")

    def aspirate(self, volume):  # volume in uL
        mL_per_step = 0.319
        steps = int(volume/mL_per_step)
        aspirate_cmd = "/1P" + str(steps) + "R\r"
        self.serial_connection.write_string(aspirate_cmd)
        time.sleep(0.05)
        self.serial_connection.wait_for_pipette(model="foreach")

    def send_drop_tip_cmd(self):
        eject_tip = "/1ER\r"
        self.serial_connection.write_string(eject_tip)
        time.sleep(0.05)
        self.serial_connection.wait_for_pipette(model="foreach")

    def dispense(self, volume=0):  # volume in uL
        dispense_all = "/1A0R\r"
        self.serial_connection.write_string(dispense_all)
        time.sleep(0.05)
        self.serial_connection.wait_for_pipette(model="foreach")

    def send_tip_check_cmd(self):
        check_tip = "/1?31R\r"
        self.serial_connection.write_string(check_tip)
        time.sleep(0.05)
        res = self.serial_connection.wait_for_pipette(model="foreach")
        return res

    def is_tip_attached(self):
        res = self.send_tip_check_cmd()
        if b"`1\x03" in res:
            print("tip attached! code:", res)
            return True
        else:
            print("tip NOT attached! code:", res)
            return False

    def send_pickup_tip_cmd(self):  # do nothing, not needed for foreach model
        pass

    def set_transport_air_volume(self, volume=50):  # volume in uL
        self.aspirate(volume)
        time.sleep(0.05)
        self.serial_connection.wait_for_pipette(model="foreach")

import sys
import time
import logging
from chem_robox.robot.drivers import serial_connection


class Pipette(object):
    def __init__(self, pipette_port):
        self.pipette_port = pipette_port

    def connect(self):
        self.serial_connection = serial_connection.Connection(
            port=self.pipette_port, baudrate=19200, parity='E')
        time.sleep(1)
        is_open = self.serial_connection.isOpen()
        if is_open:
            logging.info("E-pipette connected")
        else:
            logging.info("E-pipette failed to connect")
        # self.initialization()

    def initialization(self):
        cmd = '00DIid0001\r\n'
        self.serial_connection.write_string(cmd)
        time.sleep(0.05)
        self.serial_connection.wait_for_pipette()
        # self.enable_anti_dropping()

    def enable_anti_dropping(self):
        cmd = '00AYid0001\r\n'  # anti drop enabled
        self.serial_connection.write_string(cmd)
        time.sleep(0.05)
        self.serial_connection.wait_for_pipette()

    def aspirate(self, volume):  # volume in uL
        cmd1 = str(volume*10)
        cmd = '00ALid0001av' + \
            cmd1.zfill(
                5)+'oa00050bv00100fr05000ss05000qm0bi0qc0000qf0000qe0000to010\r\n'
        self.serial_connection.write_string(cmd)
        time.sleep(0.05)
        self.serial_connection.wait_for_pipette()

    def set_transport_air_volume(self, volume=50):  # volume in uL
        cmd = "00ATid0001tv"+str(volume*10).zfill(5)+"fr02000\r\n"
        self.serial_connection.write_string(cmd)
        time.sleep(0.05)
        self.serial_connection.wait_for_pipette()

    def send_pickup_tip_cmd(self):  # volume in uL
        cmd = '00TPid0001tt06\r\n'
        self.serial_connection.write_string(cmd)
        time.sleep(0.05)
        self.serial_connection.wait_for_pipette()

    def send_drop_tip_cmd(self):  # volume in uL
        cmd = '00TDid0001\r\n'
        self.serial_connection.write_string(cmd)
        time.sleep(0.05)
        self.serial_connection.wait_for_pipette()

    def dispense(self, volume):  # volume in uL
        cmd1 = str(volume*10)
        cmd = '00DLid0001dv' + \
            cmd1.zfill(5)+'sv080fr05000ss05000qm0bi0qc0000qf0000qe0000to010\r\n'
        cmd = '00DEid0001\r\n'  # fr05000ss05000qm0bi0qc0000qf0000qe0000to010\r\n'
        # empty tip cmd DE
        self.serial_connection.write_string(cmd)
        time.sleep(0.05)
        self.serial_connection.wait_for_pipette()

    def send_tip_check_cmd(self):
        cmd = '00RTid0001\r\n'
        self.serial_connection.write_string(cmd)
        time.sleep(0.05)
        res = self.serial_connection.wait_for_pipette()
        return res

    def is_tip_attached(self):
        res = self.send_tip_check_cmd()
        if "rt1" in res:
            print("tip attached! code:", res)
            return True
        else:
            print("tip NOT attached! code:", res)
            return False
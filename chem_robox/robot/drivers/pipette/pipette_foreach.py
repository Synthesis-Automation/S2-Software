# import sys
import time
import logging
from chem_robox.robot.drivers import serial_connection

# Hardware interface of Foreach pipette (http://foreachtek.com/en/ProductInfo.aspx?Id=10517)

WAIT_TIME = 0.1

class Pipette(object):
    def __init__(self, pipette_port):
        self.pipette_port = pipette_port

    def connect(self):
        self.serial_connection = serial_connection.Connection(
            port=self.pipette_port, baudrate=38400)
        time.sleep(1)
        is_open = self.serial_connection.isOpen()
        if is_open:
            print("E-pipette connected")
        else:
            logging.info("E-pipette failed to connect")
            print("E-pipette failed to connect")

    def wait_for_response(self):
        while True:
            time.sleep(WAIT_TIME)
            msg = self.serial_connection.serial_port.readline()
            if msg:
                print("Got response.", msg)
                return msg

    def wait_for_finish(self):
        query_cmd = "/1Q\r"
        i = 1
        while True:
            self.serial_connection.send_commond_string_foreach(query_cmd)
            time.sleep(WAIT_TIME)
            res = self.serial_connection.serial_port.readline()
            if not (b'/0@\x03' in res):
                print(i, res)
            i = i+1
            if i > 300:
                print("Pipette no response for 30 seconds, system exited")
                # sys.exit()
            if b'/0`' in res:
                print("Finish request.")
                return "finish"

    def send_commond_string_foreach(self, cmd):
        self.wait_for_finish()
        self.serial_connection.send_commond_string_foreach(cmd)

    def initialization(self):
        init_cmd = '/1ZR\r'
        self.send_commond_string_foreach(init_cmd)
        time.sleep(1)
        self.wait_for_response()
        self.wait_for_finish()
        print("initialization finished.")
        normal_mode = "/1N0R\r"
        # N0 mode and N1 mode
        self.send_commond_string_foreach(normal_mode)
        self.wait_for_response()
        self.wait_for_finish()

    def increase_range(self):
        cmd = '/1u1,3500R\r'
        self.send_commond_string_foreach(cmd)
        self.wait_for_response()
        self.wait_for_finish()

    def aspirate(self, volume):
        '''aspirate volume = ? uL'''
        mL_per_step = 0.319
        steps = int(volume/mL_per_step)
        aspirate_cmd = "/1P" + str(steps) + "R\r"
        self.send_commond_string_foreach(aspirate_cmd)
        self.wait_for_response()
        self.wait_for_finish()

    def send_drop_tip_cmd(self):
        eject_tip = "/1ER\r"
        self.send_commond_string_foreach(eject_tip)
        time.sleep(0.5)
        self.wait_for_response()
        self.wait_for_finish()

    def dispense(self, volume=0):  # volume in uL
        dispense_all = "/1A0R\r"
        self.send_commond_string_foreach(dispense_all)
        self.wait_for_response()
        self.wait_for_finish()

    def set_speed(self, speed):
        '''speed = 0-40, default = 11, bigger nmuber is slower '''
        cmd = "/1S" + str(speed) + "R\r"
        self.send_commond_string_foreach(cmd)
        self.wait_for_response()
        self.wait_for_finish()

    def is_tip_attached(self):
        check_tip_cmd = "/1?31R\r"
        self.send_commond_string_foreach(check_tip_cmd)
        res = self.wait_for_response()
        self.wait_for_finish()
        if b"`1\x03" in res:
            print("tip attached! code:", res)
            return True
        else:
            print("tip NOT attached! code:", res)
            return False

    def send_pickup_tip_cmd(self):  # do nothing, not needed for foreach model
        pass

    def set_transport_air_volume(self, volume=20):  # volume in uL
        if volume > 0:
            self.aspirate(volume)

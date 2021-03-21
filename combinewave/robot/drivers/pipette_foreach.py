import sys
import time
import logging
from combinewave.robot.drivers import serial_connection

# Hardare interface of Foreach pipette (http://foreachtek.com/en/ProductInfo.aspx?Id=10517)
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
            logging.info("E-pipette connected")
        else:
            print("E-pipette failed to connect")
            logging.info("E-pipette failed to connect")

    def wait_for_response(self):
        msg = self.serial_connection.readline_string(timeout=10)
        print(msg)
        return msg

    def wait_for_finish(self):
        query_cmd = "/1Q\r"
        while True:
            self.serial_connection.send_commond_string(query_cmd)
            time.sleep(0.05)
            res = self.serial_connection.readline_string()
            print(res, end="")
            if '/0`' in res:
                print("finsih")
                return "finsih"

    def initialization(self):
        init_cmd = '/1ZR\r'
        self.serial_connection.send_commond_string(init_cmd)
        self.wait_for_response()
        self.wait_for_finish()
        normal_mode = "/1N0R\r"
        # N0 mode and N1 mode
        self.serial_connection.send_commond_string(normal_mode)
        self.wait_for_response()

    def aspirate(self, volume):
        '''aspirate volume = ? uL'''
        mL_per_step = 0.319
        steps = int(volume/mL_per_step)
        aspirate_cmd = "/1P" + str(steps) + "R\r"
        self.serial_connection.send_commond_string(aspirate_cmd)
        self.wait_for_response()
        self.wait_for_finish()

    def send_drop_tip_cmd(self):
        eject_tip = "/1ER\r"
        self.serial_connection.send_commond_string(eject_tip)
        self.wait_for_response()
        self.wait_for_finish()

    def dispense(self, volume=0):  # volume in uL
        dispense_all = "/1A0R\r"
        self.serial_connection.send_commond_string(dispense_all)
        self.wait_for_response()
        self.wait_for_finish()

    def is_tip_attached(self):
        check_tip = "/1?31R\r"
        self.serial_connection.send_commond_string(check_tip)
        res = self.wait_for_response()        
        if "`1\x03" in res:
            print("tip attached! code:", res)
            return True
        else:
            print("tip NOT attached! code:", res)
            return False

    def send_pickup_tip_cmd(self):  # do nothing, not needed for foreach model
        pass

    def set_transport_air_volume(self, volume=50):  # volume in uL
        self.aspirate(volume)


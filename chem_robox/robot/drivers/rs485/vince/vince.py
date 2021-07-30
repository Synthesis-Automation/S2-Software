#!/usr/bin/env python
import time

import struct

def float_to_hex(f):
    return hex(struct.unpack('<I', struct.pack('<f', f))[0])

class vince():
    def __init__(self, modbus_connection, unit=7):
        self.modbus_client = modbus_connection.client
        self.unit = unit

    def enable_motor(self):
        # enable motor
        self.modbus_client.write_register(
            address=0x00, count=1, unit=self.unit, value=0x0101)

    def disable_motor(self):
        # disable motor
        self.modbus_client.write_register(
            address=00, count=1, unit=self.unit, value=0x0100)

    def move_to(self, x, wait_for_finish = True):
        data = [int(x)]
        self.modbus_client.write_registers(
            address=0x01, unit=self.unit, values=data)
        self.wait_for_finish()


    def set_speed(self, speed):
        # when speed = 10000.0, data = [0x4000, 0x461c]
        # hex_str = 0x461c4000 as a string
        hex_str = float_to_hex(speed)
        high_hex_str = '0x'+ hex_str[2:6]
        low_hex_str = '0x' + hex_str[6:10]
        high = int(high_hex_str, 0)
        low = int(low_hex_str, 0)
        data = [low, high]
        self.modbus_client.write_registers(
            address=0x03, unit=self.unit, values=data)

    def get_status(self, address, count=1):
        response = self.modbus_client.read_holding_registers(
            address=address, count=count, unit=self.unit)
        if not response.isError():
            print(response.registers)
            return response.registers
        else:
            # Handle Error
            print("Error reading")
            return False

    def set_baudrate(self, baudrate):
        # rate = int(baudrate)
        # data = rate.to_bytes(4, 'big')
        # for i in range(50):
        #     rd = self.modbus_client.read_holding_registers(address=i, count=1, unit=self.unit)
        #     print(rd.registers)
        # # rd = self.modbus_client.read_holding_registers(address=10, count=10, unit=self.unit)
        # # print(rd.registers)
        # # rd = self.modbus_client.read_holding_registers(address=20, count=10, unit=self.unit)
        # # print(rd.registers)
        data = [0xc200, 0x0001]
        self.modbus_client.write_registers(
            address=32, unit=self.unit, values=data)

    def read_sensor_S1(self, address=4):
        response = self.modbus_client.read_input_registers(
            address=address, count=1, unit=self.unit)
        # time.sleep(0.5)    
        if not response.isError():
            # get the last digital in a binary number
            state = response.registers[0] % 2
            print('sensor state: ', state)
            return state
        else:
            # Handle Error
            print("Error reading sensor S1")
            return(False)

    def read_state(self, address=4):
        response = self.modbus_client.read_input_registers(
            address=address, count=1, unit=self.unit)
        if not response.isError():
            # get the last digital in a binary number
            state = response.registers[0]
            return int(str(bin(state))[-9])
        else:
            # Handle Error
            print("Error reading sensor S1")
            return(False)


    def wait_for_finish(self):
        i = 0
        while i < 1000:
            state = self.read_state()
            if state == 1:
                return "finish"
        print("Time out")

    def home(self):
        # init
        self.modbus_client.write_register(
            address=0x0100, value=0x0001, unit=self.unit)



#!/usr/bin/env python
import time
WAIT_TIME = 0.1

class Gripper():
    def __init__(self, modbus_connection, unit=1):
        self.modbus_client = modbus_connection.client
        self.unit = unit

    def initialization(self):
        self.modbus_client.write_register(
            address=0x0100, value=0x0001, unit=self.unit)
        time.sleep(WAIT_TIME)
        self.set_rotation_force(90)
        self.set_rotation_speed(percent=95)
        time.sleep(WAIT_TIME)
        self.rotate_position = 0
        self.set_gripper_force(99)
        self.gripper_close(50)
        self.rotate(720)

    def gripper_open(self, percent):  # percentage of gripper open
        distance = int(percent*10)
        self.modbus_client.write_register(
            address=0x0103, value=distance, unit=self.unit)
        timer = 1
        while True:
            time.sleep(WAIT_TIME)
            timer = timer + 1
            if self.get_gripper_status() == 1:  # 1 indicate reach the target position
                return True
            if timer > 20:
                return False

    def gripper_close(self, percent):  # percentage of gripper open
        distance = int(percent*10)
        self.modbus_client.write_register(
            address=0x0103, value=distance, unit=self.unit)
        timer = 1
        while True:
            time.sleep(WAIT_TIME)
            timer = timer + 1
            status = self.get_gripper_status()
            results = {
                0: "still moving",
                1: "gripper stopped, No object was holded",
                2: "gripper stopped, object was holded",
                3: "object lost"
            }
            print(f"griper close, return code: {status}, {results[status]}")
            if status == 2:  # 2 indicate holding of targets
                return True
            if timer > 30:
                return False

    def is_gripper_holding(self):  # percentage of gripper open
        status = self.get_gripper_status()
        results = {
            0: "still moving",
            1: "gripper stopped, No object was holded",
            2: "gripper stopped, object was holded",
            3: "object lost"
        }
        print(f"griper status: return code= {status}, {results[status]}")
        if status != 1:
            return True
        else:
            return False

    def rotate_to(self, degree):  # 360 degree = 1 cicle
        time.sleep(WAIT_TIME)
        self.modbus_client.write_register(
            address=0x0105, value=degree, unit=self.unit)
        # timer = 1
        # while True:
        #     time.sleep(WAIT_TIME)
        #     timer = timer + 1
        #     if self.get_rotation_status() in [1, 2, 3]:
        #         return True
        #     if timer > 50:
        #         return False

    def rotate(self, degree):  # 360 degree = 1 cicle
        time.sleep(WAIT_TIME)
        current = self.get_rotation_position()
        print(f'current: {current}, degree: {degree}')
        self.rotate_to(current+degree)

    def read(self, address=0, count=1):
        response = self.modbus_client.read_holding_registers(
            address=address, count=count, unit=self.unit)  # unit is the id of device
        return response.registers[0]

    def get_rotation_status(self):
        response = self.modbus_client.read_holding_registers(
            address=0x020B, count=1, unit=self.unit)  # unit is the id of device
        status = response.registers[0]
        results = {
            0: "still moving",
            1: "reach target position",
            2: "stopped by force",
            3: "reach target position, stopped by force during the process"
        }
        print(f"rotation_status: return code= {status}, {results[status]}")
        return status

    def is_rotation_ok(self):  # percentage of gripper open
        # self.rotate(15)
        while True:
            status = self.get_rotation_status()
            if status in [2, 3]:
                return False
            elif status == 1:
                return True

    def get_gripper_status(self):
        response = self.modbus_client.read_holding_registers(
            address=0x0201, count=1, unit=self.unit)  # unit is the id of device
        status = response.registers[0]
        return status

    def get_gripper_position(self):
        rr = self.modbus_client.read_holding_registers(
            address=0x0103, count=1, unit=self.unit)  # unit is the id of device
        return rr.registers[0]

    def set_gripper_force(self, percent=50):  # fron 20-100 percent
        time.sleep(WAIT_TIME)
        self.modbus_client.write_register(
            address=0x0101, value=percent, unit=self.unit)

    def get_rotation_position(self):
        time.sleep(WAIT_TIME)
        rr = self.modbus_client.read_holding_registers(
            address=0x0105, count=1, unit=self.unit)  # unit is the id of device
        return rr.registers[0]

    def set_rotation_speed(self, percent=30):
        time.sleep(WAIT_TIME)
        self.modbus_client.write_register(
            address=0x0107, value=percent, unit=self.unit)

    def set_rotation_force(self, percent=50):  # fron 20-100 percent
        time.sleep(WAIT_TIME)
        self.modbus_client.write_register(
            address=0x0108, value=percent, unit=self.unit)

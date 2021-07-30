from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import time
import sys
import logging

class RS485():
    def __init__(self, port='', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.connect()

    def connect(self):
        self.client = ModbusClient(method='rtu', port=self.port, timeout=1,
                                   stopbits=1, bytesize=8,  parity='N', baudrate=self.baudrate)
        for i in range(6):
            response = self.client.connect()
            if response:
                return
            else:
                print("Tring to connect modbus again...")
                time.sleep(1)
                if i >= 5:
                    print('Modbus connection failed, quit program!')
                    logging.info("Modbus connection failed")
                    sys.exit()

    def close(self):
        self.client.close()

    def other(self):
        self.client.readwrite_registers()

import time
from chem_robox.robot.drivers import rs485_connection
from chem_robox.robot.drivers.rs485.vince import vince

connection = rs485_connection.RS485(port='com10', baudrate=115200)

motor = vince.vince(modbus_connection = connection, unit=7)
time.sleep(0.1)

motor.set_speed(10000)
time.sleep(0.01)
motor.enable_motor()
motor.move_to(20000)

# time.sleep(5)
motor.move_to(0)
# time.sleep(3)
# # motor.disable_motor()

for i in range(1000):
    s = motor.read_state()
    print(s)


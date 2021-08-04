import time


'''
Response from Marlin
start
Marlin 2.0.9.1

echo: Last Updated: 2021-06-27 | Author: (none, default config)
echo:Compiled: Jul 15 2021
echo: Free Memory: 5727  PlannerBufferBytes: 1152
echo:Hardcoded Default Settings Loaded
echo:  G21    ; Units in mm (mm)

echo:; Filament settings: Disabled
echo:  M200 S0 D1.75

echo:; Steps per unit:
echo: M92 X80.00 Y80.00 Z400.00 E500.00
test system: microstepping 16, screw 4 mm step_per_mm = 200x16/4 = 800

echo:; Maximum feedrates (units/s):
echo:  M203 X300.00 Y300.00 Z5.00 E25.00

echo:; Maximum Acceleration (units/s2):
echo:  M201 X3000.00 Y3000.00 Z100.00 E10000.00

echo:; Acceleration (units/s2): P<print_accel> R<retract_accel> T<travel_accel>
echo:  M204 P3000.00 R3000.00 T3000.00

echo:; Advanced: B<min_segment_time_us> S<min_feedrate> T<min_travel_feedrate> J<junc_dev>
echo:  M205 B20000.00 S0.00 T0.00 J0.01

echo:; Home offset:
echo:  M206 X0.00 Y0.00 Z0.00

echo:; PID settings:
echo:  M301 P22.20 I1.08 D114.00
'''
# xy_platform.set_speed(x=9000, y=6000)  # 10000 will lose steps
# xy_platform.set_acceleration(x=600, y=600)  # default 1200 mm/sec2 600 for us
# print(xy_platform.smoothie.speeds)
# print(xy_platform.smoothie.get_steps_per_mm('x'))
# print(xy_platform.smoothie.get_steps_per_mm('y'))


class Marlin_driver(object):

    """
    This object uses GCode for motion control based on Marlin firmare
    """

    MOVE = 'G0'
    DWELL = 'G4'
    HOME = 'G28.2'
    SET_ZERO = 'G28.3'
    GET_POSITION = 'M114.2'
    GET_TARGET = 'M114.4'
    GET_ENDSTOPS = 'M119'
    HALT = 'M112'
    CALM_DOWN = 'M999'
    SET_SPEED = 'M203.1'
    SET_ACCELERATION = 'M204'
    MOTORS_ON = 'M17'
    MOTORS_OFF = 'M18'
    AXIS_AMPERAGE = 'M907'
    STEPS_PER_MM = 'M92'

    PUSH_SPEED = 'M120'
    POP_SPEED = 'M121'  

    ABSOLUTE_POSITIONING = 'G90'
    RELATIVE_POSITIONING = 'G91'

    FAN_ON = "M106"  #Turn on the fan at 200/255 DC: M106 S200
    FAN_OFF = "M107"
    # M206 - Set Home Offsets M206 X10

    # M220 - Set Feedrate Percentage: M220 S100

    """
    Serial port connection to talk to the device.
    """
    connection = None

    def __init__(self):
        self.current_commands = []

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def connect(self, serial_connection):
        self.connection = serial_connection
        self.toggle_port()
        time.sleep(1)
        self.connection.flush_input()

    def is_connected(self):
        if self.connection:
            return self.connection.isOpen()
        return False

    def toggle_port(self):
        self.connection.close()
        self.connection.open()
        self.connection.serial_pause()
        self.connection.flush_input()

    def ignore_next_line(self):
        self.connection.readline_string()

    def readline_from_serial(self, timeout=5):
        """
        Attempt to read a line of data from serial port

        Raises RuntimeWarning if read fails on serial port
        """
        self.connection.wait_for_data(timeout=timeout)
        msg = self.connection.readline_string()
        return msg

    def send_command(self, command):
        cmd = command.upper() + "\r\n"
        self.connection.write_string(cmd)

    def move_to(self, **kwargs):
        attempts = 0
        max_attempts = 6
        move_sent = False
        args = ' '.join(['{}{}'.format(k, v) for k, v in kwargs.items()])
        while attempts <= max_attempts and (not move_sent):
            attempts += 1
            move_line = self.MOVE + " " + args.upper() + "\r\n"
            m400 = "M400"
            self.send_command(move_line+m400)
            self.wait_for_finish()
            move_sent = True
            break
        self.wait_for_finish()

    def wait_for_finish(self, finish_code="ok", timeout=30):
        while True:
            self.connection.wait_for_data(timeout=timeout)
            msg = self.connection.readline_string()
            # print("waiting: ", msg)
            if finish_code in msg:
                print("Finished.")
                return True
            else:
                print("Not finish yet, response: ", msg)
                # return False

    def home(self, axes):
        # e.g., axis = "xy"
        cmd = "G28"
        for axis in axes:
            cmd = cmd + " " + axis
        self.send_command(cmd)
        self.wait_for_finish()

    def get_current_position(self):
        # return format: {"x": x, "y": y, "z": z, "a": a}
        self.send_command(self.GET_POSITION)
        current_string = self.readline_from_serial()
        self.wait_for_finish()
        xyz = self._parse_coordinates(current_string)
        return xyz

    def set_acceleration(self, **kwargs):
        cmd = "M201"  
        for axis, acceleration in kwargs.items():
            cmd = cmd + " " + axis + str(acceleration)
        self.send_command(cmd)
        self.wait_for_finish()

    def set_steps_per_mm(self, axis, steps_per_mm):
        cmd = "M92" + " " + axis + str(steps_per_mm)
        self.send_command(cmd)
        self.wait_for_finish()

    def set_speed(self, **kwargs):
        cmd = "M203"
        for axis, speed in kwargs.items():
            cmd = cmd + " " + axis + str(speed)
        self.send_command(cmd)
        self.wait_for_finish()

    def _parse_coordinates(self, string):
        # print(string)
        parsed_values = string.split(' ')
        # print(parsed_values)
        x = float(parsed_values[0].split(":")[1])
        y = float(parsed_values[1].split(":")[1])
        z = float(parsed_values[2].split(":")[1])
        a = float(parsed_values[3].split(":")[1])
        coordinates = {"x": x, "y": y, "z": z, "a": a}
        return coordinates

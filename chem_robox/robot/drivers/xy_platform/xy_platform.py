from chem_robox.robot.drivers import serial_connection
from chem_robox.robot.drivers.xy_platform import marlin_driver, smoothie_drivers
from chem_robox import parameters
MARLIN_SPEED_MULTIPLIER = 32

class XY_platform():
    def __init__(self, port='', baudrate=115200, head_offsets={}, firmware="Smoothie"):
        self.port = port
        self.baudrate = baudrate
        self.head_offsets = head_offsets
        self.stop_flag = False
        self.firmware = firmware

    def connect(self):
        c = serial_connection.Connection(
            port=self.port, baudrate=self.baudrate)
        if self.firmware == "Marlin":
            self.motion_control = marlin_driver.Marlin_driver()
        else:
            self.motion_control = smoothie_drivers.SmoothieDriver()
        self.motion_control.connect(c)
        if self.firmware == "Marlin":
            self.motion_control.set_steps_per_mm(axis = 'x', steps_per_mm = 5120)
            self.motion_control.set_steps_per_mm(axis = 'y', steps_per_mm = 5120)
            self.set_speed(x=300/MARLIN_SPEED_MULTIPLIER, y=200/MARLIN_SPEED_MULTIPLIER)
            self.set_acceleration(x=80, y=20) # 100 is stable

    def update(self, head_offsets={}):
        self.head_offsets = head_offsets

    def set_speed(self, *args, **kwargs):
        self.motion_control.set_speed(*args, **kwargs)

    def set_steps_per_mm(self, *args, **kwargs):  # 2500 mm/min
        self.motion_control.set_steps_per_mm(*args, **kwargs)

    def set_acceleration(self, **kwargs):  # 1200 mm/sec2, may add axis in the future   
        self.motion_control.set_acceleration(**kwargs)

    def home_x(self):
        self.motion_control.home('x')

    def home_y(self):
        self.motion_control.home('y')

    def home(self, axis):  # axis ='xyzab'
        self.motion_control.home(axis)

    def get_position(self, axis='x'):  # axis = 'x', 'y'
        if self.firmware == "Marlin":
            pos = self.motion_control.get_current_position()
            coordinate = pos[axis]*MARLIN_SPEED_MULTIPLIER
        else:
            coordinate = self.motion_control.get_target_position()[
                axis]*2  # smoothie_pos
        return coordinate

    def get_position_all(self):
        # get coordinated of all axes
        if self.firmware == "Marlin":
            pos = self.motion_control.get_current_position()
        else:
            pos = self.motion_control.get_target_position()
        return pos

    def move_to(self, head='Z1', vial={}):
        # Vial data format: {'x': 11.14, 'y': 62.04, 'z': 0, 'depth': 85, ...}
        # the smoothieware has a strange problem which limit the highest speed,
        # We have to work around by double the steps_per_mm for x and y
        # For marlin, we have to use 8*
        if self.stop_flag:
            return False
        if self.firmware == "Marlin":
            x = (vial['x'] + self.head_offsets[head][0])/MARLIN_SPEED_MULTIPLIER
            y = (vial['y'] + self.head_offsets[head][1])/MARLIN_SPEED_MULTIPLIER
        else:
            x = (vial['x'] + self.head_offsets[head][0])/2
            y = (vial['y'] + self.head_offsets[head][1])/2
        self.motion_control.move_to(x=x, y=y)
        return True

    def move(self, x=0, y=0, z=0, a=0, b=0):
        x1 = self.get_position("x")
        y1 = self.get_position("y")
        X = (x+x1)/MARLIN_SPEED_MULTIPLIER
        Y = (y+y1)/MARLIN_SPEED_MULTIPLIER
        self.motion_control.move_to(x=X, y=Y)

    def mosfet_engage(self, index):
        """
        Engages the MOSFET.
        """
        self.motion_control.set_mosfet(index, True)

    def mosfet_disengage(self, index):
        """
        Disengages the MOSFET.
        """
        self.motion_control.set_mosfet(index, False)

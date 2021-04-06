from combinewave.robot.drivers import serial_connection
from combinewave.robot.drivers.xy_platform import smoothie_drivers
from combinewave import parameters


class XY_platform():
    def __init__(self, port='', baudrate=115200, head_offsets={}):
        self.port = port
        self.baudrate = baudrate
        self.head_offsets = head_offsets
        self.stop_flag = False

    def connect(self):
        c = serial_connection.Connection(
            port=self.port, baudrate=self.baudrate)
        self.smoothie = smoothie_drivers.SmoothieDriver()
        self.smoothie.connect(c)
        self.smoothie.prevent_squeal_on_boot()
        self.set_acceleration(x=600, y=400)  # default 1200 mm/sec2 600 for us
        self.set_speed(x=8000, y=6000)  # 10000 will lose steps

    def update(self, head_offsets={}):
        self.head_offsets = head_offsets

    def set_speed(self, *args, **kwargs):  # 2500 mm/min
        self.smoothie.set_speed(*args, **kwargs)

    def set_acceleration(self, **kwargs):  # 1200 mm/sec2, may add axe in the future
        self.smoothie.set_acceleration(**kwargs)

    def home_x(self):
        self.smoothie.home('x')

    def home_y(self):
        self.smoothie.home('y')

    def home(self, axe):  # axe ='xyzab'
        self.smoothie.home(axe)

    def get_position(self, axe='x'):  # axe = 'x', 'y'
        return self.smoothie.get_target_position()[axe]*2

    def move_to(self, head='Z1', vial={}):
        # Vial data format: {'x': 11.14, 'y': 62.04, 'z': 0, 'depth': 85, ...}
        # the smoothieware has a strange problem which limit the highest speed,
        # We have to work around by double the steps_per_mm for x and y
        if self.stop_flag:
            return False
        plate = vial['plate']
        x = vial['x'] + self.head_offsets[head][0]
        y = vial['y'] + self.head_offsets[head][1]
        self.smoothie.move_head(mode='absolute', x=x/2, y=y/2)
        return True

    def move(self, x=0, y=0, z=0, a=0, b=0):
        self.smoothie.move_head(mode='relative', x=x/2, y=y/2, z=z, a=a, b=b)

    def mosfet_engage(self, index):
        """
        Engages the MOSFET.
        """
        self.smoothie.set_mosfet(index, True)

    def mosfet_disengage(self, index):
        """
        Disengages the MOSFET.
        """
        self.smoothie.set_mosfet(index, False)

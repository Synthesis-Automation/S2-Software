import math
import json

from builtins import property as _property, tuple as _tuple
from operator import itemgetter as _itemgetter
from collections import OrderedDict

import time
from threading import Event


class VectorValue(tuple):
    """
    # from collections import namedtuple
    # value_type = namedtuple('VectorValue', ['x', 'y', 'z'])
    """
    'VectorValue(x, y, z)'

    __slots__ = ()

    _fields = ('x', 'y', 'z')

    def __new__(_cls, x, y, z):
        'Create new instance of VectorValue(x, y, z)'
        return _tuple.__new__(_cls, (x, y, z))

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new VectorValue object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 3:
            raise TypeError('Expected 3 arguments, got %d' % len(result))
        return result

    def _replace(_self, **kwds):
        """Return a new VectorValue object replacing specified fields with
        new values
        """
        result = _self._make(map(kwds.pop, ('x', 'y', 'z'), _self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % list(kwds))
        return result

    def __repr__(self):
        'Return a nicely formatted representation string'
        return self.__class__.__name__ + '(x=%r, y=%r, z=%r)' % self

    def _asdict(self):
        'Return a new OrderedDict which maps field names to their values.'
        return OrderedDict(zip(self._fields, self))

    def __getnewargs__(self):
        'Return self as a plain tuple.  Used by copy and pickle.'
        return tuple(self)

    x = _property(_itemgetter(0), doc='Alias for field number 0')

    y = _property(_itemgetter(1), doc='Alias for field number 1')

    z = _property(_itemgetter(2), doc='Alias for field number 2')


value_type = VectorValue


# To keep Python 3.4 compatibility
def isclose(a, b, rel_tol):
    return abs(a - b) < rel_tol


class VectorEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Vector):
            return dict(zip('xyz', obj))
        try:
            return json.JSONEncoder.default(self, obj)
        except Exception:
            return str(obj)


class Vector(object):
    zero_vector = None

    @classmethod
    def zero_coordinates(cls):

        if not cls.zero_vector:
            cls.zero_vector = value_type(0, 0, 0)

        return cls.zero_vector

    @classmethod
    def coordinates_from_dict(cls, dictionary):
        kwargs = {}
        for axis in 'xyz':
            kwargs[axis] = dictionary.get(axis, 0)
        return value_type(**kwargs)

    @classmethod
    def coordinates_from_iterable(cls, iterable):
        return value_type(
            iterable[0],
            iterable[1],
            iterable[2])

    def to_iterable(self):
        return self.coordinates

    def to_tuple(self):
        return self.coordinates

    def is_iterable(self, arg):
        return hasattr(arg, "__iter__") or hasattr(arg, "__getitem__")

    def length(self):
        return math.sqrt(
            pow(self.coordinates.x, 2) +
            pow(self.coordinates.y, 2) +
            pow(self.coordinates.z, 2)
        )

    def __init__(self, *args, **kwargs):
        # self.coordinates = self.zero_coordinates()

        args_len = len(args)
        if args_len == 1:
            arg = args[0]
            if isinstance(arg, dict):
                self.coordinates = Vector.coordinates_from_dict(arg)
            elif isinstance(arg, Vector):
                self.coordinates = arg.coordinates
            elif self.is_iterable(arg):
                self.coordinates = Vector.coordinates_from_iterable(arg)
            else:
                raise ValueError(
                    ("One argument supplied "
                     "expected to be dict or iterable, received {}")
                    .format(type(arg)))
        elif args_len == 3:
            self.coordinates = value_type(*args)
        else:
            raise ValueError("Expected either a dict/iterable or x, y, z")

    def __eq__(self, other):
        if isinstance(other, Vector):
            return all(
                [isclose(a, b, rel_tol=1e-5)
                 for a, b in zip(self, other)]
            )
        elif isinstance(other, dict):
            return self == Vector(other)
        elif self.is_iterable(other):
            return self == Vector(other)
        else:
            raise ValueError("Expected operand to be dict, iterable or vector")

    def __add__(self, other):
        other = other
        return Vector(
            self.coordinates.x + other[0],
            self.coordinates.y + other[1],
            self.coordinates.z + other[2]
        )

    def __sub__(self, other):
        other = other
        return Vector(
            [a - b for a, b in zip(self, other)])

    def __truediv__(self, other):
        if isinstance(other, Vector):
            return Vector(
                [a / b for a, b in zip(self, other)])

        scalar = float(other)
        return self / Vector(scalar, scalar, scalar)

    def __mul__(self, other):
        if isinstance(other, Vector):
            return Vector(
                [a * b for a, b in zip(self, other)])

        scalar = float(other)
        return self * Vector(scalar, scalar, scalar)

    def __str__(self):
        return "(x={:.2f}, y={:.2f}, z={:.2f})".format(
            self.coordinates.x,
            self.coordinates.y,
            self.coordinates.z,
        )

    def __repr__(self):
        return str(self)

    def __getitem__(self, index):
        res = None
        if isinstance(index, int):
            res = self.coordinates[index]
        elif isinstance(index, str):
            res = getattr(self.coordinates, index)
        elif isinstance(index, slice):
            res = self.coordinates[index]
        else:
            raise IndexError('Expected slice or string as an index')

        return res

    def __iter__(self):
        return iter(self.to_tuple())
# ______________


class SmoothieDriver(object):

    """
    This object outputs raw GCode commands to perform high-level tasks.
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

    RESET = 'reset'

    ABSOLUTE_POSITIONING = 'G90'
    RELATIVE_POSITIONING = 'G91'

    COMMANDS_TO_RECORD = [
        ABSOLUTE_POSITIONING, RELATIVE_POSITIONING, MOVE, DWELL, HOME,
        SET_ZERO, SET_SPEED, SET_ACCELERATION, PUSH_SPEED, POP_SPEED,
        MOTORS_ON, MOTORS_OFF, AXIS_AMPERAGE
    ]

    CONFIG_GET = 'config-get sd'
    CONFIG_SET = 'config-set sd'
    OT_VERSION = 'ot_version'
    GET_FIRMWARE_VERSION = 'version'
    CONFIG_VERSION = 'version'
    CONFIG_STEPS_PER_MM = {
        'x': 'alpha_steps_per_mm',
        'y': 'beta_steps_per_mm',
        'z': 'gamma_steps_per_mm'
    }

    MOSFET = [
        {True: 'M41', False: 'M40'},
        {True: 'M43', False: 'M42'},
        {True: 'M45', False: 'M44'},
        {True: 'M47', False: 'M46'},
        {True: 'M49', False: 'M48'},
        {True: 'M51', False: 'M50'}
    ]

    """
    Serial port connection to talk to the device.
    """
    connection = None

    def __init__(self):
        self.halted = Event()
        self.stopped = Event()
        self.do_not_pause = Event()
        self.resume()
        self.current_commands = []

        self.SMOOTHIE_SUCCESS = 'Success'
        self.SMOOTHIE_ERROR = 'Received unexpected response from Smoothie'
        self.STOPPED = 'Received a STOP signal and exited from movements'

        self.ignore_smoothie_sd = False

        self.config_dict = {}

        self.default_speeds = {}
        self.ot_one_dimensions = {}
        self.speeds = {}

        self.smoothie_player = None

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def connect(self, smoothie_connection):
        self.connection = smoothie_connection
        self.toggle_port()
        self.calm_down()
        #log.debug("Connected to {}".format(self.connection.name()))

    def prevent_squeal_on_boot(self):
        # TODO: (andy) Smoothieware EDGE has this weird bug,
        # seems to require the following commands to run after Smoothieboard
        # boots, or else all motors freeze up and make high-pitch sounds.
        # This is simply sending a tiny move command, then halt, then resume
        self.send_command('G91 G0 X0.001', read_after=False)
        self.wait_for_ok()
        self.send_halt_command()
        self.calm_down()

    def prevent_squeal_after_home(self, axis):
        # TODO: (andy) Smoothieware EDGE has this weird bug,
        # after homing an AB axis, trying to do an absolute (G90) move
        # on that axis will create a high-pitched squeel. Then
        # any following command will work fine.
        # The below move commands are meant to force Smoothieware
        # through this bug without affecting the robot's physical position
        axis = [ax for ax in axis if ax.upper() in 'AB']
        for ax in axis:
            self.move(**{ax.lower(): 1 / 1600})
            self.move(**{ax.lower(): 0.0})

    def is_connected(self):
        if self.connection:
            return self.connection.isOpen()
        return False

    def toggle_port(self):
        if not self.connection:
            raise RuntimeError('Not connected to robot')
        self.connection.close()
        self.connection.open()
        self.connection.serial_pause()
        self.connection.flush_input()

    def wait_for_ok(self):
        res = self.readline_from_serial()
        if res != 'ok':
            raise RuntimeError(
                '{0}: {1}'.format(self.SMOOTHIE_ERROR, res))

    def ignore_next_line(self):
        self.connection.readline_string()

    def readline_from_serial(self, timeout=3):
        """
        Attempt to read a line of data from serial port

        Raises RuntimeWarning if read fails on serial port
        """
        self.connection.wait_for_data(timeout=timeout)
        msg = self.connection.readline_string()
        if msg:
            #log.debug("Read: {}".format(msg))
            self.detect_smoothie_error(str(msg))
        return msg

    # THREADING
    def pause(self):
        self.halted.clear()
        self.stopped.clear()
        self.do_not_pause.clear()

    def resume(self):
        self.halted.clear()
        self.stopped.clear()
        self.do_not_pause.set()

    def stop(self):
        self.halted.clear()
        self.stopped.set()
        self.do_not_pause.set()

    def halt(self):
        self.halted.set()
        self.stopped.set()
        self.do_not_pause.set()

    def send_command(
            self,
            command,
            read_after=True,
            timeout=3,
            m400=False,
            **kwargs):
        """
        Sends a GCode command.  Keyword arguments will be automatically
        converted to GCode syntax.

        Returns a string with the Smoothie board's response
        Empty string if no response from Smoothie

        send_command(self.MOVE, x=100 y=100)
        G0 X100 Y100

        appends M400 if m400=True. This will cause smoothie to send 'ok'
        only after it empties the queue (finishes making a move).
        """
        #log.debug('sending {} command w/timeout = {}'.format(command, timeout))
        if not self.is_connected():
            self.toggle_port()

        m400_cmd = 'M400' if m400 else ''

        args = ' '.join(['{}{}'.format(k, v) for k, v in kwargs.items()])
        gcode_line = '{} {} {}\r\n'.format(command, args, m400_cmd)
        #log.debug("Write: {}".format(gcode_line))

        self.connection.flush_input()
        self.connection.write_string(gcode_line)

        if read_after:
            return self.readline_from_serial(timeout=timeout)

    def detect_smoothie_error(self, msg):
        """
        Detect if it hit a home switch

        Raises RuntimeWarning if Smoothie reports a limit hit
        """
        if 'reset or M999' in msg or 'error:' in msg:
            self.calm_down()
            time.sleep(0.2)  # pause for Smoothie's internal state change
            self.calm_down()
            error_msg = 'Robot Error: limit switch hit'
            # log.debug(error_msg)
            raise RuntimeWarning(error_msg)

    def convert_relative_coords_to_absolute(self, **kwargs):
        for axis in 'xyz':
            current = self.get_head_position()['target']
            kwargs[axis] = kwargs.get(axis, 0) + current[axis]
        for axis in 'ab':
            current = self.get_plunger_positions()['target']
            kwargs[axis] = kwargs.get(axis, 0) + current[axis]
        return kwargs

    def move(self, mode='absolute', **kwargs):
        # Convert relative coordinates to absolute coordinates
        if mode == 'relative':
            mode = 'absolute'
            kwargs = self.convert_relative_coords_to_absolute(**kwargs)

        self.set_coordinate_system(mode)
        self.set_speed()

        current = self.get_head_position()['target']
        target_point = {
            axis: kwargs.get(
                axis,
                0 if mode == 'relative' else current[axis]
            )
            for axis in 'xyz'
        }
        flipped_vector = self.flip_coordinates(
            Vector(target_point), mode)
        for axis in 'xyz':
            kwargs[axis] = flipped_vector[axis]

        args = {axis.upper(): kwargs.get(axis)
                for axis in 'xyzab'
                if axis in kwargs}
        #args.update({"F": max(list(self.speeds.values()))})

        attempts = 0
        max_attempts = 7
        move_sent = False
        while attempts <= max_attempts and (not move_sent):
            attempts += 1
            try:
                self.send_command(self.MOVE, **args, m400=True, timeout=300)
                self.wait_for_ok()
                move_sent = True
                break
            except RuntimeWarning as e:
                raise e
            except Exception as e:
                reconnect_delay = attempts ** 2
                time.sleep(reconnect_delay)
                self.reconnect_driver()

        if not move_sent:
            raise RuntimeWarning(
                'Failed to complete move command after {} tries'
                .format(attempts)
            )

        arguments = {
            'name': 'move-finished',
            'position': {
                'head': self.get_head_position()["current"],
                'plunger': self.get_plunger_positions()["current"]
            },
            'class': type(self.connection).__name__
        }

    def reconnect_driver(self):
        try:
            self.connection.reconnect()
        except OSError:
            #log.info('Driver failed to reconnect')
            pass

    def move_plunger(self, mode='absolute', **kwargs):
        self.move(mode, **kwargs)

    def move_head(self, mode='absolute', **kwargs):
        self.move(mode, **kwargs)

    def flip_coordinates(self, coordinates, mode='absolute'):
        coordinates = Vector(coordinates) * Vector(1, 1, 1)
        #coordinates = Vector(coordinates) * Vector(1, -1, -1)
        ''' 
        if mode == 'absolute':
            offset = Vector(0, 1, 1) * self.ot_one_dimensions[self.ot_version]
            coordinates += offset'''
        return coordinates

    def home(self, *axis):

        self.calm_down()

        axis_to_home = ''
        for a in axis:
            ax = ''.join(sorted(a)).upper()
            if ax in 'ABXYZ':
                axis_to_home += ax
        if not axis_to_home:
            return

        try:
            self.send_command(self.HOME + axis_to_home, read_after=False)
            self.connection.wait_for_data(timeout=20)
            self.connection.flush_input()
            self.send_command(self.SET_ZERO + axis_to_home, read_after=False)
            self.connection.wait_for_data(timeout=20)
            self.connection.flush_input()
        except Exception:
            raise RuntimeWarning(
                'HOMING ERROR: Check switches are being pressed and connected')

        self.prevent_squeal_after_home(axis_to_home)

    def set_coordinate_system(self, mode):
        if mode == 'absolute':
            self.send_command(self.ABSOLUTE_POSITIONING)
        elif mode == 'relative':
            self.send_command(self.RELATIVE_POSITIONING)
        else:
            raise ValueError('Invalid coordinate mode: ' + mode)
        self.wait_for_ok()

    def calm_down(self):
        self.send_command(self.CALM_DOWN, read_after=False)
        self.ignore_next_line()
        self.ignore_next_line()
        self.connection.serial_pause()
        self.connection.flush_input()

    def send_halt_command(self):
        self.send_command(self.HALT, read_after=False)
        self.connection.serial_pause()
        self.connection.flush_input()

    def reset(self):
        res = self.send_command(self.RESET)
        if 'Rebooting' in res:
            self.wait_for_ok()
            self.disconnect()

    def get_head_position(self):
        coords = self.get_position()
        coords['current'] = self.flip_coordinates(Vector(coords['current']))
        coords['target'] = self.flip_coordinates(Vector(coords['target']))
        return coords

    def get_position(self):
        return {
            'current': self.get_current_position(),
            'target': self.get_target_position()
        }

    def get_current_position(self):
        # ok MCS: X:0.0000 Y:0.0000 Z:0.0000 A:0.0000 B:0.0000 C:0.0000
        current_string = self.send_command(self.GET_POSITION)
        self.wait_for_ok()
        return self._parse_axis_values(current_string)

    def get_target_position(self):
        # ok MP: X:0.0000 Y:0.0000 Z:0.0000 A:0.0000 B:0.0000 C:0.0000
        target_string = self.send_command(self.GET_TARGET)
        self.wait_for_ok()
        return self._parse_axis_values(target_string)

    def set_acceleration(self, **kwargs):
        axis = {
            ax.upper(): val
            for ax, val in kwargs.items()
            if ax.upper() in 'XYZABC'
        }
        self.send_command(self.SET_ACCELERATION, **axis)
        self.wait_for_ok()

    def set_speed(self, *args, **kwargs):
        if len(args) > 0:
            self.speeds.update({'x': args[0], 'y': args[0]})
        self.speeds.update({l: kwargs[l] for l in 'xyzab' if l in kwargs})
        if self.is_connected():
            kwargs = {
                key.upper(): int(val / 60)  # M203.1 is in mm/sec (not mm/min)
                for key, val in self.speeds.items()
            }
            self.send_command(self.SET_SPEED, **kwargs)
            self.wait_for_ok()

    def calibrate_steps_per_mm(self, axis, expected_travel, actual_travel):
        current_steps_per_mm = self.get_steps_per_mm(axis)
        current_steps_per_mm *= (expected_travel / actual_travel)
        current_steps_per_mm = round(current_steps_per_mm, 2)
        self.set_steps_per_mm(axis, current_steps_per_mm)

    def get_steps_per_mm(self, axis):
        if axis.lower() not in 'xyzab':
            raise ValueError('Axis {} not supported'.format(axis))

        res = self.send_command(self.STEPS_PER_MM)
        self.wait_for_ok()
        self.wait_for_ok()
        return self._parse_axis_values(res).get(axis.lower())

    def set_steps_per_mm(self, axis, value):
        if axis.lower() not in 'xyz':
            raise ValueError('Axis {} not supported'.format(axis))

        res = self.send_command(self.STEPS_PER_MM, **{axis.upper(): value})
        self.wait_for_ok()
        self.wait_for_ok()

        returned_value = self._parse_axis_values(res).get(axis.lower())
        key = self.CONFIG_STEPS_PER_MM[axis.lower()]
        self.set_config_value(key, str(returned_value))

    def get_endstop_switches(self):
        # X_min:0 Y_min:0 Z_min:0 A_min:0 B_min:0 pins- (XL)P1.24:0 .......
        endstop_values = self.send_command(self.GET_ENDSTOPS)
        self.wait_for_ok()
        self.wait_for_ok()

        # ['X_min:0', 'Y_min:0', 'Z_min:0', 'A_min:0', 'B_min:0']
        endstop_values = endstop_values.split(' ')[:5]
        return {
            endstop[0].lower(): bool(int(endstop.split(':')[1]))
            for endstop in endstop_values
        }

    def set_mosfet(self, mosfet_index, state):
        try:
            command = self.MOSFET[mosfet_index][bool(state)]
            res = self.send_command(command)
            return res == 'ok'
        except IndexError:
            raise IndexError(
                "Smoothie mosfet not at index {}".format(mosfet_index))

    def power_on(self):
        self.send_command(self.MOTORS_ON)
        self.wait_for_ok()

    def power_off(self):
        self.send_command(self.MOTORS_OFF)
        self.wait_for_ok()

    def read_config_file(self):
        self.config_dict = {}
        for line in self.read_sd_file('config').split('\n'):
            data = line.split('#')[0].strip()
            data = [d.strip() for d in data.split(' ') if len(d)]
            if len(data):
                self.config_dict[data[0]] = data[1]

    def read_sd_file(self, filename, timeout=30):
        self.send_command(
            'cat /sd/{}'.format(filename),
            read_after=False)

        file_string = ''
        end_time = time.time() + timeout
        while end_time > time.time():
            data = self.readline_from_serial()
            if 'file not found' in data.lower():
                raise RuntimeError('Smoothie Error: {}'.format(data))
            elif data == 'ok':
                return file_string
            file_string += '{}\r\n'.format(data)

    def get_config_value(self, key):
        if not self.config_dict:
            self.read_config_file()
        return self.config_dict.get(key)

    def set_config_value(self, key, value):
        command = '{0} {1} {2}'.format(self.CONFIG_SET, key, value)
        self.send_command(command)
        self.wait_for_ok()  # ignore second 'ok'
        self.read_config_file()

    def versions_compatible(self):
        self.get_ot_version()
        self.get_firmware_version()
        self.get_config_version()
        res = {
            'firmware': True,
            'config': True,
            'ot_version': True
        }
        if self.firmware_version not in self.compatible_firmware:
            res['firmware'] = False
        if self.config_file_version not in self.compatible_config:
            res['config'] = False
        if self.ot_version not in self.ot_one_dimensions:
            res['ot_version'] = False

        if not all(res.values()):
            raise RuntimeError(
                'This Robot\'s versions are incompatible with the API: '
                'firmware={firmware}, '
                'config={config}, '
                'ot_version={ot_version}'.format(
                    firmware=self.firmware_version,
                    config=self.config_file_version,
                    ot_version=self.ot_version
                )
            )
        return res

    def get_ot_version(self):
        self.ot_version = False
        if not self.ot_version:
            res = self.get_config_value(self.OT_VERSION)
            if res not in self.ot_one_dimensions:
                #log.debug('{} is not an ot_version'.format(res))
                return None
            self.ot_version = res
            if not self.speeds:
                self.speeds = self.default_speeds[self.ot_version]
        return self.ot_version

    def get_plunger_positions(self):
        coords = self.get_position()
        plunger_coords = {}
        for state in ['current', 'target']:
            plunger_coords[state] = {
                axis: coords[state].get(axis, 0)
                for axis in 'ab'
            }
        return plunger_coords

    def get_firmware_version(self):
        self.firmware_version = False
        if not self.firmware_version:
            # Build version: BRANCH-HASH, Build date: Mar 18 2017 21:15:21, MCU: LPC1769, System Clock: 120MHz  # noqa
            #   CNC Build 6 axis
            #   6 axis
            # ok
            line_1 = self.send_command(self.GET_FIRMWARE_VERSION)
            self.connection.readline_string()
            self.connection.readline_string()
            self.wait_for_ok()

            # uses the "branch-hash" portion as the version response
            self.firmware_version = line_1.split(',')[0].split(' ')[-1]
        return self.firmware_version

    def get_config_version(self):
        if not self.config_file_version:
            res = self.get_config_value(self.CONFIG_VERSION)
            self.config_file_version = res
        return self.config_file_version

    def get_dimensions(self):
        if not self.ot_version:
            self.get_ot_version()
        return self.ot_one_dimensions[self.ot_version]

    def get_baudrate(self):
        return int(self.connection.serial_port.baudrate)

    def get_timeout(self):
        return float(self.connection.serial_port.timeout)

    def get_port(self):
        return str(self.connection.serial_port.port)

    def _apply_defaults(self, defaults_file):

        DEFAULT_VERSIONS = defaults_file['versions']
        DEFAULT_MODELS = json.loads(defaults_file['models']['ot_versions'])

        self.compatible_firmware = json.loads(DEFAULT_VERSIONS['firmware'])
        self.compatible_config = json.loads(DEFAULT_VERSIONS['config'])

        for key in DEFAULT_MODELS.keys():
            axis_size = Vector(DEFAULT_MODELS[key]['dimensions'])
            self.ot_one_dimensions[key] = axis_size
            self.default_speeds[key] = DEFAULT_MODELS[key]['speeds']

    def _parse_axis_values(self, string):
        try:
            parsed_values = string.split(' ')
            if parsed_values[0] == 'ok':
                parsed_values = parsed_values[2:]
            return {
                s.split(':')[0].lower(): float(s.split(':')[1])
                for s in parsed_values
            }
        except ValueError as e:
            #log.critical("Error parsing position string from smoothie board:")
            # log.critical(string)
            raise ValueError(e) from e

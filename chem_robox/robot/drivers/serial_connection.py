import time
import serial
from serial import SerialException
import serial.tools.list_ports


def int_to_bytes(x):
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')


class Connection(object):
    def __init__(self, port='', parity=serial.PARITY_NONE, baudrate=9600, timeout=0.02):
        sp = serial.Serial()
        sp.parity = parity
        sp.port = port
        sp.baudrate = baudrate
        sp.timeout = timeout
        self.serial_port = sp
        self.open()

    def device(self):
        return self.serial_port

    def name(self):
        return str(self.serial_port.port)

    def open(self):
        if self.serial_port.isOpen():
            self.serial_port.close()
        # time.sleep(0.2)
        self.serial_port.open()

    def close(self):
        self.serial_port.close()

    def isOpen(self):
        return self.serial_port.isOpen()

    def serial_pause(self):
        time.sleep(self.serial_port.timeout)

    def data_available(self):
        return int(self.serial_port.in_waiting)

    def flush_input(self):
        while self.data_available():
            self.serial_port.reset_input_buffer()
            self.serial_pause()

    def wait_for_data(self, timeout=20):
        end_time = time.time() + timeout
        while end_time > time.time():
            if self.data_available():
                return
        raise RuntimeWarning(
            'No data after {} second(s)'.format(timeout))

    def readline_string(self, timeout=20):
        end_time = time.time() + timeout
        while end_time > time.time():
            self.wait_for_data(timeout=timeout)
            try:
                res = str(self.serial_port.readline().decode().strip())
            except SerialException:
                self.close()
                self.open()
                return self.readline_string(timeout=end_time - time.time())
            if res:
                return res
        raise RuntimeWarning(
            'No new msg line from serial port after {} second(s)'.format(timeout))

    def write_string(self, data_string):
        self.serial_port.write(data_string.encode())
        self.serial_port.flush()

    def send_commond_string(self, data_string):
        self.flush_input()
        self.serial_port.write(data_string.encode())
        self.serial_port.flush()

    def send_commond_string_foreach(self, data_string):
        # self.flush_input()
        self.serial_port.write(data_string.encode())
        self.serial_port.flush()

    def send_command(
            self,
            command):
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
        # if not self.is_connected():
        #     self.toggle_port()

        # m400_cmd = 'M400' if m400 else ''

        # args = ' '.join(['{}{}'.format(k, v) for k, v in kwargs.items()])
        cmd_line = command+"\r\n"
        self.flush_input()
        self.write_string(cmd_line)

        # if read_after:
        #     return self.readline_from_serial(timeout=timeout)

    def wait_for_finish(self):
        while True:
            msg = self.readline_string()
            if 'finish' in msg:
                return(True)
            elif 'error' in msg:
                print("error occurs (serial port)")
                return(False)

    def wait_for_pipette(self, model="hamilton"):
        '''Wait unitl hamilton pipette send back its response'''
        if model == "hamilton":
            while True:
                msg = self.readline_string()
                print(msg)
                error_code = msg.split("er", 1)[-1]
                if error_code == 0:
                    print('Pipette response OK')
                    return(msg)
                elif 'er' in msg:
                    print("error code: ", error_code)
                    return(error_code)
                if 'id' in msg:
                    return msg


def get_port_by_VID(vid):
    '''Returns first serial device with a given VID'''
    for d in serial.tools.list_ports.comports():
        if d.vid == vid:
            return d[0]


def get_port_by_serial_no(sn):
    '''Returns first serial device with a given serial_no'''
    for d in serial.tools.list_ports.comports():
        if d.serial_number == sn:
            return d[0]


def get_all_ports():
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        print("{}: {} [{}]".format(port, desc, hwid))


if __name__ == "__main__":
    vid_xy_platform = 0x1D50
    vid_z_platform = 0x1A86
    vid_pipette = 0x10C4  # CP210x
    vid_modbus = 0x10C4  # CP210x, PID 0xEA60, DTECH
    vid_waveshare = 0x0403  # FT232, PID 0x6001
    vid_ika = 0x0483

    sn_pipette = '8C9CF2DFF27FEA119526CA1A09024092'
    sn_modbus = 'D2B376D8C37FEA11A2BCCA1A09024092'

    # print("List of serial port")
    # ports = get_serial_ports_list()
    # if ports:
    #     print("Found", ports[0])
    # else:
    #     print('No port found')
    # ports = serial.tools.list_ports.comports()
    # print(ports)
    # for d in serial.tools.list_ports.comports():
    #     print(d.vid, d.pid, d.device, d.serial_number)

    get_all_ports()
    # sn_waveshare = "AH0704GQA"
    # sn = "14014012AF6998A25E3FFDBCF50020C0"
    # sn_ugreen = "AR0KH8VEA"
    # sn_z_tek = "FT9L1TAQA"
    # sn_iocrest = "DA005415A"
    # com_port = get_port_by_serial_no(sn_ugreen)
    # print(com_port)

    xy_platform_port = get_port_by_VID(vid_xy_platform)
    z_platform_port = get_port_by_VID(vid_z_platform)
    # modbus_port = get_port_by_VID(vid_modbus)
    # pipette_port = get_port_by_VID(vid_pipette)
    modbus_port = get_port_by_serial_no(sn_modbus)
    pipette_port = get_port_by_serial_no(sn_pipette)

    usb_info = f"xy_port= {xy_platform_port}, z_port= {z_platform_port}, modbus_port= {modbus_port}, pipette_port= {pipette_port}"
    print(usb_info)

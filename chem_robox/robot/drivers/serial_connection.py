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

    def send_command(self, command):
        """
        Sends a GCode command, adding a "\r\n" to the end. 
        """
        cmd_line = command+"\r\n"
        self.flush_input()
        self.write_string(cmd_line)

    def wait_for_finish(self):
        while True:
            msg = self.readline_string()
            if 'finish' in msg:
                return(True)
            elif 'error' in msg:
                print("error occurs (serial port)")
                return(False)

def get_port_by_VID(vid):
    '''Returns first serial device with a given VID'''
    for d in serial.tools.list_ports.comports():
        if d.vid == vid:
            return d[0]

def get_port_by_VID_list(vid_string_list):
    '''Returns first serial device with a VID list, VID was given as hex string, e.g. '0x126b' '''
    for d in serial.tools.list_ports.comports():
        for vid in vid_string_list:
            if d.vid == int(vid ,16):
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
    vid_xy_platform = int("0x1D50", 16)
    vid_z_platform = int("0x1A86", 16)
    vid_pipette = 0x10C4  # CP210x
    vid_modbus = 0x10C4  # CP210x, PID 0xEA60, DTECH
    vid_waveshare = 0x0403  # FT232
    vid_ika = 0x0483
    vid_list = ["0x1D50", "0x067B"]

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

    xy_platform_port = get_port_by_VID(vid_xy_platform)
    z_platform_port = get_port_by_VID(vid_z_platform)
    print("z_platform_port:", z_platform_port)
    # modbus_port = get_port_by_VID(vid_modbus)
    # pipette_port = get_port_by_VID(vid_pipette)
    modbus_port = get_port_by_serial_no(sn_modbus)
    pipette_port = get_port_by_serial_no(sn_pipette)

    usb_info = f"xy_port= {xy_platform_port}, z_port= {z_platform_port}, modbus_port= {modbus_port}, pipette_port= {pipette_port}"
    print(usb_info)

    usb_port = get_port_by_VID_list(vid_list)
    print(usb_port)
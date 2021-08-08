import json
import sys
import time
from pathlib import Path
from chem_robox.robot.drivers.z_platform import z_platform
from chem_robox import parameters
from chem_robox.deck import deck
from chem_robox.robot.drivers.serial_connection import get_port_by_VID_list, get_port_by_serial_no

robot_config_file = Path("chem_robox/config/robot_config.json")
with open(robot_config_file) as config:
    robot_config = json.load(config)
my_deck = deck.Deck(robot_config)
head_offsets = my_deck.head_offsets
# Convert a string to a hex nmuber (VID)
usb_vid_z_platform = robot_config["usb_serial_VID"]["z_platform"]
z_platform_port = get_port_by_VID_list(usb_vid_z_platform)

z_platform = z_platform.Z_platform(port=z_platform_port, head_offsets=head_offsets)
z_platform.connect()


for i in range(10):
    a = z_platform.get_position(head="Z1")
    print(i, a)


z_platform.home(head='Z1')
z_platform.home(head='Z2')
z_platform.home(head='Z3')

z_platform.pickup_tablet()
input("pickup")
z_platform.drop_tablet()
DISTANCE = 200
# for i in range(5):
#     z_platform.move(head="Z1", z=-1*DISTANCE)
#     z_platform.move(head="Z1", z=DISTANCE)
#     z_platform.move(head="Z2", z=-1*DISTANCE)
#     z_platform.move(head="Z2", z=DISTANCE)
#     z_platform.move(head="Z3", z=-1*DISTANCE)
#     z_platform.move(head="Z3", z=DISTANCE)

# z_platform.move_to_abs(head="Z2", z=3)

# z_platform.pickup_tablet(z=50)

# z_platform.set_max_speed(head='Z1', speed=500)

# z_platform.move_to(head="Z1", z=20)

# z_platform.set_max_speed(head='Z1', speed=4000)

# z_platform.move_to(head="Z1", z=5)


# z_platform.home(head='Z1')

# z_platform.home(head='Z1')
# z_platform.home(head='Z2')
# z_platform.home(head='Z3')

# z_platform.move(head="Z1", z=50)
# z_platform.move(head="Z2", z=-4)

# z_platform.move_to(head="Z2", z=DISTANCE)
# z_platform.move(head="Z2", z=5)
# z_platform.move(head="Z3", z=-4)

#
# z_platform.pickup_tablet()

# z_platform.drop_tablet()

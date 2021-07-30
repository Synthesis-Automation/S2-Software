import json, sys
import time
from pathlib import Path
from chem_robox.robot.drivers.z_platform import z_platform
from chem_robox import parameters
from chem_robox.deck import deck

robot_config_file = Path("chem_robox/config/robot_config.json")
with open(robot_config_file) as config:
    robot_config = json.load(config)
my_deck = deck.Deck(robot_config)
head_offsets = my_deck.head_offsets
deck = deck.Deck(robot_config)

z_platform = z_platform.Z_platform(port='com15', head_offsets=deck.head_offsets)
z_platform.connect()


for i in range(5000):
    a = z_platform.get_position(head = "Z1")
    print(i, a)

# z_platform.home(head='Z1')
# z_platform.home(head='Z2')
# z_platform.move_to(head = "Z2", z=50)
# z_platform.move_to_abs(head = "Z2", z=3)


# z_platform.pickup_tablet(z=50)

# z_platform.set_max_speed(head='Z1', speed=500)

# z_platform.move_to(head="Z1", z=20)

# z_platform.set_max_speed(head='Z1', speed=4000)

# z_platform.move_to(head="Z1", z=5)

# z_platform.drop_tablet()

# z_platform.home(head='Z1')

# z_platform.home(head='Z1')
# z_platform.home(head='Z2')
# z_platform.home(head='Z3')

# z_platform.move(head="Z1", z=50)
# z_platform.move(head="Z2", z=-4)

# z_platform.move_to(head="Z2", z=30)
# z_platform.move(head="Z2", z=5)
# z_platform.move(head="Z3", z=-4)

# 
# z_platform.pickup_tablet()

# z_platform.drop_tablet()
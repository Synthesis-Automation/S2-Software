import json, sys
import time
from combinewave.robot.drivers.z_platform import z_platform
from combinewave import parameters
from combinewave.deck import deck

deck = deck.Deck()

z_platform = z_platform.Z_platform(port='com11', head_offsets=deck.head_offsets)
z_platform.connect()

z_platform.home(head='Z1')
z_platform.home(head='Z2')
z_platform.move_to(head = "Z2", z=50)
z_platform.move_to_abs(head = "Z2", z=3)


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
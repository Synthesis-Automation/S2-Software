import json, sys
import time
from combinewave.robot.drivers.z_platform import z_platform
from combinewave import parameters
from combinewave.deck import deck
robot_config = {
        "note": "refenrence is compared to conner of slot A1, Z is to deck surface",
        "max_robot_rows": 3,
        "max_robot_cols": 5,
        "col_offset": 134,
        "row_offset": 92,
        "max_number_of_plate": 15,        
        "reference": {
            "x": 0,
            "y": 0,
            "z": 120
        },
        "slots": {
            "A1": { "x": 0, "y": 0 },
            "A2": { "x": 134, "y": 0 },
            "A3": { "x": 268, "y": 0 },
            "A4": { "x": 402, "y": 0 },
            "A5": { "x": 536, "y": 0 },
            "B1": { "x": 0, "y": 92 },
            "B2": { "x": 134, "y": 92 },
            "B3": { "x": 268, "y": 92 },
            "B4": { "x": 402, "y": 92 },
            "B5": { "x": 536, "y": 92 },
            "C1": { "x": 0, "y": 184 },
            "C2": { "x": 134, "y": 184 },
            "C3": { "x": 268, "y": 184 },
            "C4": { "x": 402, "y": 184 },
            "C5": { "x": 536, "y": 184 }
        },

        "steps_per_mm_Z1": 100,
        "steps_per_mm_Z2": 100,
        "steps_per_mm_Z3": 100,
        "steps_per_mm_X": 100,
        "steps_per_mm_Y": 100,

        "pipette_model": "foreach",
        "gripper_model": "flexrobo",

        "usb_sn_xy_platform": "14014012AF6998A25E3FFDBCF50020C0",
        "usb_sn_z_platform": "",
        "usb_sn_pipette":"8C9CF2DFF27FEA119526CA1A09024092",
        "usb_sn_modbus": "D2B376D8C37FEA11A2BCCA1A09024092"
        }

deck = deck.Deck(robot_config)

z_platform = z_platform.Z_platform(port='com10', head_offsets=deck.head_offsets)
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
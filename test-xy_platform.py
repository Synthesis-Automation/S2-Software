from chem_robox.robot.drivers.xy_platform import xy_platform, smoothie_drivers
from chem_robox.deck import deck
from pathlib import Path
import json

# test code for this module      
if __name__ == '__main__':
    robot_config_file = Path("chem_robox/config/robot_config.json")
    with open(robot_config_file) as config:
        robot_config = json.load(config)
    my_deck = deck.Deck(robot_config)
    head_offsets = my_deck.head_offsets

    USB_port = 'com5'
    xy_platform = xy_platform.XY_platform(
        port=USB_port, head_offsets=head_offsets, firmware="Marlin")
    xy_platform.connect()

    # For Fuyu linear module, 20 mm/sec will lose steps
    # xy_platform.set_steps_per_mm(axis='x', steps_per_mm=1600)
    # xy_platform.set_steps_per_mm(axis='y', steps_per_mm=1600)
    # xy_platform.set_speed(x=18, y=18)
    # xy_platform.set_acceleration(x= 1000, y = 1000)

    # # XY linear module, 20 mm/sec will lose steps
    # xy_platform.motion_control.set_steps_per_mm(axis='x', steps_per_mm=160)
    # xy_platform.motion_control.set_steps_per_mm(axis = 'y', steps_per_mm = 160)
    # xy_platform.set_speed(x=50, y=50)
    # xy_platform.set_acceleration(x= 1000, y = 1000)

    # xy_platform.home('xy')
    # xy_platform.home("x")

    # Lower level control
    # for i in range(1):
    #     # input("continue")
    #     print(i)
    #     xy_platform.motion_control.move_to(x=100,  y=0)
    #     print("go back")
    #     xyz = xy_platform.motion_control.get_current_position()
    #     print(xyz)
    #     xy_platform.motion_control.move_to(x=10,  y=0)
    #     xyz = xy_platform.motion_control.get_current_position()
    #     print(xyz)

    vial_1 = my_deck.vial(plate='R1', vial='A1')
    vial_1 = {'x': 3.805, 'y': 1.9, 'z': 0, 'depth': 59.0, 'plate': 'R1', 'vial': 'A1', 'type': 'reactor_square_8mL_20p', 'height': 166.0, 'diameter': 18.0}
    vial_2 = my_deck.vial(plate='R1', vial='A5')
    print(vial_2)
    for i in range(2):
        xy_platform.move_to(vial=vial_1)
        xy_platform.move_to(vial=vial_2)
    print('Done')

    # for i in range(10):
    #     xy_platform.mosfet_engage(index_1)   # 2 is for the fan (top one)
    #     time.sleep(0.5)
    #     xy_platform.mosfet_disengage(index_1)
    #     time.sleep(0.5)
    #     xy_platform.mosfet_engage(index_2)   # 2 is for the fan (top one)
    #     time.sleep(0.5)
    #     xy_platform.mosfet_disengage(index_2)
    #     time.sleep(0.5)

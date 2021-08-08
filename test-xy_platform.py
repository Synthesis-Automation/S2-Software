from chem_robox.robot.drivers.xy_platform import xy_platform
from chem_robox.deck import deck
from pathlib import Path
import json
from chem_robox.robot.drivers.serial_connection import get_port_by_VID_list, get_port_by_serial_no


# test code for this module      
if __name__ == '__main__':

    robot_config_file = Path("chem_robox/config/robot_config.json")
    with open(robot_config_file) as config:
        robot_config = json.load(config)
    my_deck = deck.Deck(robot_config)
    head_offsets = my_deck.head_offsets
    usb_vid_xy_platform = robot_config["usb_serial_VID"]["xy_platform"]
    xy_platform_port = get_port_by_VID_list(usb_vid_xy_platform)
    print(xy_platform_port)

    xy_platform = xy_platform.XY_platform(
        port=xy_platform_port, head_offsets=head_offsets, firmware="Marlin")
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

    # xy_platform.home('x')
    xy_platform.home('xy')


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
    # vial_1 = {'x': 3.805, 'y': 1.9, 'z': 0, 'depth': 59.0, 'plate': 'R1', 'vial': 'A1', 'type': 'reactor_square_8mL_20p', 'height': 166.0, 'diameter': 18.0}
    # vial_2 = {'x': 600, 'y': 280, 'z': 0, 'depth': 59.0, 'plate': 'R1', 'vial': 'A1', 'type': 'reactor_square_8mL_20p', 'height': 166.0, 'diameter': 18.0}
    vial_1 = {'x': 3.805, 'y': 1.9, 'z': 0, 'depth': 59.0, 'plate': 'R1', 'vial': 'A1', 'type': 'reactor_square_8mL_20p', 'height': 166.0, 'diameter': 18.0}
    vial_2 = {'x': 600, 'y': 280, 'z': 0, 'depth': 59.0, 'plate': 'R1', 'vial': 'A1', 'type': 'reactor_square_8mL_20p', 'height': 166.0, 'diameter': 18.0}
    vial_3 = {'x': 600, 'y': 1.9, 'z': 0, 'depth': 59.0, 'plate': 'R1', 'vial': 'A1', 'type': 'reactor_square_8mL_20p', 'height': 166.0, 'diameter': 18.0}

    print(vial_2)
    xy_platform.move_to(vial=vial_2)
    for i in range(5):
        xy_platform.move_to(vial=vial_3)
        xy_platform.move_to(vial=vial_2)
        xy_platform.move_to(vial=vial_1)
    
    # for i in range(5):
    #     xy_platform.move(x = 650)
    #     xy_platform.move(x = -650)


    # for i in range(5):
    #     xy_platform.move(y = 50)
    #     xy_platform.move(y = -50)
    

    # print('Done')

    # # for i in range(10):
    # #     xy_platform.mosfet_engage(index_1)   # 2 is for the fan (top one)
    # #     time.sleep(0.5)
    # #     xy_platform.mosfet_disengage(index_1)
    # #     time.sleep(0.5)
    # #     xy_platform.mosfet_engage(index_2)   # 2 is for the fan (top one)
    # #     time.sleep(0.5)
    # #     xy_platform.mosfet_disengage(index_2)
    # #     time.sleep(0.5)

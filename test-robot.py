# coding:utf-8
from pathlib import Path

from chem_robox import parameters
from chem_robox.robot import robot
from chem_robox.tools import helper
from chem_robox.deck import deck

# CAPPER = 'Z1'... defined in parameters.py
from chem_robox.parameters import CAPPER, LIQUID, TABLET


def capper_test(plate, plate_type):
    my_deck = deck.Deck()
    cap_list = my_deck.get_vial_list_by_plate_type(plate_type)
    print(cap_list)
    for cap in cap_list:
        chem_robot.decap((plate, cap))
        chem_robot.recap((plate, cap))

def tablet_test():
    vial_from = ("C2", "D7")
    vial_to = ("C3", "A1")
    chem_robot.transfer_tablet(vial_from, vial_to, number_of_tablet=11)
    

if __name__ == "__main__":
    chem_robot = robot.Robot()
    chem_robot.connect()
    chem_robot.home_all()
    chem_robot.move_to(vial = ("R1", "A1"))
    # capper_test("B2", plate_type = "plate_5mL")
    # capper_test("C3", plate_type = "plate_8mL")
    # capper_test("A3", plate_type = "plate_40mL")
    # chem_robot.gripper.rotate_to(450)
    # tablet_test()




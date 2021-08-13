from chem_robox.deck import deck
from pathlib import Path
import json

# test code for this module
if __name__ == '__main__':

    robot_config_file = Path("chem_robox/config/robot_config.json")
    with open(robot_config_file) as config:
        robot_config = json.load(config)
    deck = deck.Deck(robot_config)
    a = deck.get_current_tip()
    b = deck.get_current_tip(format="A1")
    print("Current tip = ", a, "or", b)

    print("deck._slots")
    print(deck._slots)
    print()

    # print("deck._plates")
    # print(deck._plates)
    # print()

    print("deck.calibration")
    print(deck.calibration)
    print()

    print("deck.head_offsets")
    print(deck.head_offsets)
    print()

    print("deck.deck_calibration_x and deck_calibration_y")
    print(deck.deck_calibration_x, deck.deck_calibration_y)
    print()

    print("vial cooridnates:")
    vial_1 = deck.vial(plate='C2', vial='A1')
    print(vial_1)

    slots = deck.slot_list
    print("slot_list:")
    print(slots)

    print("slot_list-2:")
    vial_list_ = deck.get_vial_list_by_plate_type("deck")
    print(vial_list_)

    print("plate_2mL cols and rows")
    res = deck.get_cols_rows_by_plate_type(plate_type="plate_2mL")
    print(res)

    current_reactor = deck.get_current_reactor()
    print("current_reactor:", current_reactor)

    current_reactor_slot = deck.get_current_reactor_slot()
    print("current_reactor_slot:", current_reactor_slot)

    current_tip_small = deck.get_current_tip(tip_type="tips_50uL")
    print("current_tip_small:", current_tip_small)

    plate_type = deck.get_plate_type_of_slot("C4")
    print(plate_type)

    GC_LC_plate = deck.get_plate_assignment("GC LC")
    print(GC_LC_plate)

    # res = deck.convert_A1_to_number_by_plate_type("A1", plate_type="plate_5mL")
    # print(res)
    # vial_list_ = deck.get_vial_list_by_slot("A2")
    # print(vial_list_)

    # plate_name = deck.get_plate_assignment("Clean up")
    # print(plate_name)
    # res = deck.convert_number_to_A1(0, plate_name)
    # print(res)
    # res = deck.convert_A1_to_number("B1", plate_name)
    # print(res)

    # print()
    # print(deck.convert_number_to_A1(number=4, plate='B3'))
    # print(deck.convert_A1_to_number("A1", plate='B3'))
    # print(deck.next_vial('B3', plate='B3'))
    # r = deck.get_assignment_of_slot("C3")
    # print(r)

    v = deck.deck_config.values()
    print(v)
    a = deck.get_plate_list()
    print(a)
    b = deck.is_plate_on_deck(plate_list = ["plate_2mL:001"])
    print(b)

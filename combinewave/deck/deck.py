# The deck module gives the cooridinates of all plates and vials placed on the deck
# It also manages robot_config
# It also manages plate definition
# It also manages calibration data

# The internal data structure of deck class, all unit is mm

# Data structure of vial generated from deck.vial(plate="A1", vial="B2"), diameter is for the cap
# {'x': 10, 'y': 10, 'z': 0, 'depth': 40, 'plate': 'A1', 'vial': 'A1', 'type': 'plate_5mL', 'diameter': 18.0}

# self.robot_config
# example: {
# "note": "reference is compared to conner of slot A1, capper:4mm, tablet 4 mm, liquid:4 mm, 56",
# "col_offset": 134,
# "row_offset": 92,
# "max_robot_rows":3,
# "max_robot_cols":5,
# "reference": [0, 0, 119.6],
# "steps_per_mm_capper": 100,
# "steps_per_mm_tablet": 100,
# "steps_per_mm_liquid": 100
# }

# deck._slots, cooridinates of conner of each slot in the deck
# {'A1': (0, 0, 0), 'A2': (134, 0, 0), 'A3': (268, 0, 0), 'A4': (402, 0, 0), 'A5': (536, 0, 0), 'B1': (0, 92, 0), 'B2': (134, 92, 0), 'B3': (268, 92, 0), 'B4': (402, 92, 0), 'B5': (536, 92, 0), 'C1': (0, 184, 0), 'C2': (134, 184, 0), 'C3': (268, 184, 0), 'C4': (402, 184, 0), 'C5': (536, 184, 0)}

# deck.calibration, the difference of each slot/plate between actual cooridinates and calcuated cooridinates
# {'A1': [0, 0, 0.0], 'A2': [0.0, 0, 0.0], 'A3': [0, 0, 0], 'A4': [0, 0, 0], 'A5': [10.0, 25.0, 0], 'B1': [0.0, 0.0, 0], 'B2': [0, 0, 0], 'B3': [0, 0, 0], 'B4': [0.0, 0, 0],
# 'B5': [0, 0, 0], 'C1': [-31.0, -1.0, 0], 'C2': [-15.5, 13.0, 0], 'C3': [-11.5, 9.0, 0], 'C4': [5.0, 1.0, 82.0], 'C5': [9.900000000000091, 6.5, 0],
# 'Z1': [0, 0, 132.1], 'Z2': [0, 0, 129.6], 'Z3': [0, 0, 125.4], 'Tips': [0, 0, 106.5], 'Ref': [0, 0, 119.6]}

# deck.head_offsets, the cooridinate difference of each head or Z-axies
# {'Z1': [111, 4, 132.1], 'Z2': [59.5, 4, 129.6], 'Z3': [0, 0, 125.4]}


# self.slot_list
# ['A1', 'A2', 'A3', 'A4', 'A5', 'B1', 'B2', 'B3', 'B4', 'B5', 'C1', 'C2', 'C3', 'C4', 'C5']

# example of self.deck_config
# {
#     "A1": {"plate": "plate_5mL:001", "assignment": "Reagent"},
#     "A2": {"plate": "plate_5mL:001", "assignment": "Reagent"},
#      ......
#     "B5": {"plate": "plate_5mL:001", "assignment": "Reagent"},
#     "C1": {"plate": "plate_5mL:001", "assignment": "Tips 1000uL"},
#     "C5": {"plate": "plate_5mL:001", "assignment": "Reagent"}
# }

# example of self._plates
# # {'A1': {'version': 1.0, 'name': 'plate_5mL', 'cornerOffsetFromSlot': {'x': 10, 'y': 10, 'z': 0}, 'columns': 8, 'rows': 5, 'wells': {'A1': {'depth': 82.7,
# 'height': 105.7, 'volume': 4000, 'shape': 'circular', 'diameter': 18.0, 'x': 10, 'y': 10, 'z': 0}, 'B1': {'depth': 82.7, 'height': 105.7, 'volume': 4000,

import json
from pathlib import Path
import time


class Deck(object):
    def __init__(self, robot_config={}):
        self.robot_config = robot_config
        self.calibration_file = Path("combinewave/config/calibration.json")
        self.deck_config_file = Path("combinewave/config/deck_config.json")
        self.load_robot_config()
        self.load_deck_config()
        self.load_calibration()
        self.setup_plates()
        self.slot_list = ['A1', 'A2', 'A3', 'A4', 'A5', 'B1', 'B2', 'B3', 'B4', 'B5', 'C1', 'C2', 'C3', 'C4', 'C5']

    def load_robot_config(self):
        self.reference = self.robot_config["reference"]
        self._slots = self.robot_config["slots"]
        self.max_number_of_plate = self.robot_config["max_number_of_plate"]

    def load_deck_config(self):
        # read deck config file
        deck_config = {}
        with open(self.deck_config_file) as deck_c:
            deck_config = json.load(deck_c)
        self.update_deck_config(deck_config)
        self.reset_current_reactor()

    def load_calibration(self):
        with open(self.calibration_file, "r") as cal:
            self.calibration = json.load(cal)
        self.update_head_offsets()
        self.current_tip = self.calibration["Current_tip"]
        self.deck_calibration_x = self.calibration["Z2"][0]-self.reference["x"]
        self.deck_calibration_y = self.calibration["Z2"][1]-self.reference["y"]

    def set_current_tip(self, tip):
        self.current_tip = tip
        self.tip_update_time = float(time.time())

    def get_current_reactor(self):
        return self.current_reactor

    def reset_current_reactor(self):
        '''reset value of current reactor from data in plate assignment'''
        reactor_slot = self.get_plate_assignment(assignment="Reactor")
        reactor_name = self.deck_config[reactor_slot]["plate"]
        self.current_reactor = reactor_name.split(':')[0]

    def save_current_tip(self):
        self.save_calibration("Current_tip", self.current_tip)

    def get_current_tip(self, format="number"):
        '''return numeric format such as 0, 1 when format = number, else return non-numeric format such as A1'''
        if format == "number":
            return self.current_tip
        else:
            return self.convert_number_to_A1_by_plate_type(self.current_tip, plate_type="tiprack_1000ul")

    def get_slot_offsets(self):
        return (self.robot_config['row_offset'],
                self.robot_config['col_offset'])

    def get_max_robot_rows(self):
        return self.robot_config['max_robot_rows']

    def get_max_robot_cols(self):
        return self.robot_config['max_robot_cols']

    def get_max_number_of_plate(self):
        # self.max_number_of_plate = self.get_max_robot_rows()*self.get_max_robot_cols()
        return self.max_number_of_plate

    def update_deck_config(self, deck_config):
        '''save the whole deck_config to file'''
        self.deck_config = deck_config
        self.setup_plates()

    def update_deck_config_one_slot(self, slot="A1", slot_config={}):
        '''update slot assignment'''
        # slot_config: {"plate": "plate_5mL:001", "assignment": "Reagent"},
        self.deck_config[slot] = slot_config

    def save_deck_config(self, deck_config=None):
        ''' save deck_config to file, if no parameter is given, the self.deck_conifig will be saved'''
        if deck_config == None:
            deck_config_save = self.deck_config
        else:
            deck_config_save = deck_config
        self.update_deck_config(deck_config_save)
        with open(self.deck_config_file, "w") as json_file:
            json.dump(deck_config_save, json_file)
        from combinewave.tools import helper
        helper.format_json_file(self.deck_config_file)

    def update_head_offsets(self):
        with open(self.calibration_file, "r") as cal:
            self.calibration = json.load(cal)
        # calculate the head_offsets from the calibration data
        # the offsets (XY) is vs Z2 (center, Tablet), but offsets (z) is vs the deck surface plane
        x1 = self.calibration["Z1"][0]-self.calibration["Z2"][0]
        y1 = self.calibration["Z1"][1]-self.calibration["Z2"][1]
        z1 = self.calibration["Z1"][2]+self.reference["z"]
        x2 = 0
        y2 = 0
        z2 = self.calibration["Z2"][2]+self.reference["z"]
        x3 = self.calibration["Z3"][0]-self.calibration["Z2"][0]
        y3 = self.calibration["Z3"][1]-self.calibration["Z2"][1]
        z3 = self.calibration["Z3"][2]+self.reference["z"]
        # z1, z2, z3 are actually the z_max (the distance between deck surface and the z-end switch)
        self.head_offsets = {
            "Z1": [x1, y1, z1],
            "Z2": [x2, y2, z2],
            "Z3": [x3, y3, z3]
        }

    def save_calibration(self, plate, calibration_data):
        '''save calibration data for one plate in the slot '''
        # example: 'plate='A1', calibration_data=[1, 20, 10.50]'
        self.calibration[plate] = calibration_data
        with open(self.calibration_file, "w") as json_file:
            json.dump(self.calibration, json_file)
        from combinewave.tools import helper
        helper.format_json_file(self.calibration_file)

    def get_slot_list(self):
        return self.slot_list

    def read_plate_definition(self, plate_definition_file='plate_5mL.json'):
        with open(plate_definition_file) as data:
            plate = json.load(data)
        return plate

    def setup_plates(self):
        ''' calculate coordinates of all vials (in a plate) on the deck'''
        self._plates = {}
        for slot in self.deck_config:  # slot = 'A1' ...
            plate_name = self.deck_config[slot]["plate"]
            plate_type = plate_name.split(':')[0]
            my_plate = self.read_plate_definition(
                plate_definition_file=Path(
                    'combinewave/config/plate_definition')
                / (plate_type + ".json"))
            self._plates.update({slot: my_plate})

    def get_plate_assignment(self, assignment="Reactor"):
        '''get plate number of an assignment (e.g., Reactor)'''
        for entry in self.deck_config:
            plate_assignment = self.deck_config[entry]["assignment"]
            if plate_assignment == assignment:
                return entry
        return False

    def get_assignment_of_slot(self, slot="A1"):
        '''get assignment of a slot (e.g., A1)'''
        return self.deck_config[slot]["assignment"]

    def vial(self, plate='B1', vial='A1'):
        # This function return x, y, z and depth of a vial, vials = plate['wells']
        depth = self._plates[plate]['wells'][vial]['depth']
        height = self._plates[plate]['wells'][vial]['height']
        diameter = self._plates[plate]['wells'][vial]['diameter']
        plate_name = self.deck_config[plate]["plate"]
        plate_type = plate_name.split(':')[0]

        # self.deck_calibration_x was calced. at self.load_calibration()
        # the final x, y, z  = plate_cooridinate + slot_coordinate + deck_calibration + plate_calibration
        # there is no z  plate_calibration
        plate_x = self._plates[plate]['wells'][vial]['x']
        plate_y = self._plates[plate]['wells'][vial]['y']

        # The above is slot
        slot_x = self._slots[plate]["x"]
        slot_y = self._slots[plate]["y"]

        X = plate_x + slot_x + self.deck_calibration_x + \
            self.calibration[plate][0]
        Y = plate_y + slot_y + self.deck_calibration_y + \
            self.calibration[plate][1]
        Z = 0
        result = {'x': X, 'y': Y, 'z': Z, 'depth': depth,
                  'plate': plate, 'vial': vial, 'type': plate_type, 'height': height, 'diameter': diameter}
        return result

    def vial_coordinate(self, plate='B1', vial='A1'):
        # This function return x, y, z and depth of a vial, vials = plate['wells']
        # Plate calibration data was not used.
        depth = self._plates[plate]['wells'][vial]['depth']
        height = self._plates[plate]['wells'][vial]['height']
        diameter = self._plates[plate]['wells'][vial]['diameter']
        plate_name = self.deck_config[plate]["plate"]
        plate_type = plate_name.split(':')[0]
        plate_x = self._plates[plate]['wells'][vial]['x']
        plate_y = self._plates[plate]['wells'][vial]['y']

        slot_x = self._slots[plate]["x"]
        slot_y = self._slots[plate]["y"]

        X = plate_x + slot_x + self.deck_calibration_x
        Y = plate_y + slot_y + self.deck_calibration_y
        Z = 0
        result = {'x': X, 'y': Y, 'z': Z, 'depth': depth,
                  'plate': plate, 'vial': vial, 'type': plate_type, 'height': height, 'diameter': diameter}
        return result

    def convert_number_to_A1(self, number, plate="A1"):
        '''convert numeric number (e.g., 2) to format like A2, the number start with 0'''
        if number == len(self._plates[plate]['ordering']):
            num = 0
        else:
            num = number
        return self._plates[plate]['ordering'][num]

    def convert_number_to_A1_by_plate_type(self, number, plate_type="plate_type"):
        '''convert numeric number (e.g., 2) to format like A2, the number start with 0'''
        return self.get_vial_list_by_plate_type(plate_type)[number]

    def convert_A1_to_number_by_plate_type(self, name, plate_type="plate"):
        '''convert numeric number (e.g., 2) to format like A2, the number start with 0'''
        return self.get_vial_list_by_plate_type(plate_type).index(name)

    def convert_A1_to_number(self, number, plate="A1"):
        '''convert format "A2" to numeric number (e.g., 2)'''
        return self._plates[plate]['ordering'].index(number)

    def get_vial_list_by_slot(self, slot="A1"):
        # generate the vial list in a plate, e.g., ["A1", "B1", ...]
        return self._plates[slot]['ordering']

    def get_vial_list_by_plate_type(self, plate_type="plate_2mL"):
        # generate the vial list in a plate, e.g., ["A1", "B1", ...]
        vial_list = []
        plate_definition = self.read_plate_definition(Path(
            'combinewave/config/plate_definition')
            / (plate_type + ".json"))
        return plate_definition['ordering']

    def get_cols_rows_by_plate_type(self, plate_type="plate_2mL"):
        # generate the vial cols_rows e.g., {"columns": 5, "rows": 6}
        plate_definition = self.read_plate_definition(Path(
            'combinewave/config/plate_definition')
            / (plate_type + ".json"))
        rows = plate_definition['rows']
        columns = plate_definition['columns']
        return {'columns': columns, 'rows': rows}

    def next_vial(self, number, plate="A1"):  # format of number:"A1"
        # This function generate position of next vial (e.g., A1 -> B1)
        no = self.convert_A1_to_number(number, plate=plate)
        next_one = self.convert_number_to_A1(no+1, plate=plate)
        return next_one

    # plate_name = "plate_5mL:001"
    def get_slot_from_plate_name(self, plate_name):
        for entry in self.deck_config:
            if self.deck_config[entry]["plate"] == plate_name:
                slot = entry
                return slot
        else:
            return False

    def check_missing_assignment(self, required_plates=["Reagent", "Reactor", "Workup",
                                                        "Tips 1000uL", "Trash", "Clean up", "Reaction caps", "GC LC"]):
        for assignment in required_plates:
            if self.get_plate_assignment(assignment) == False:
                return assignment
        return "complete"


# test code for this module
if __name__ == '__main__':
    robot_config = {
        "note": "refenrence is compared to conner of slot A1, Z is to deck surface",

        "max_robot_rows": 3,
        "max_robot_cols": 5,
        "col_offset": 140,
        "row_offset": 100,
        "max_number_of_plate": 15,

        "reference": {
            "x": 149,
            "y": 108,
            "z": 172
        },

        "slots": {
            "A1": {"x": 0, "y": 0},
            "A2": {"x": 140, "y": 0},
            "A3": {"x": 290, "y": 0},
            "A4": {"x": 491, "y": 0},
            "A5": {"x": 631, "y": 0},
            "B1": {"x": 0, "y": 100},
            "B2": {"x": 140, "y": 100},
            "B3": {"x": 420, "y": 0},
            "B4": {"x": 491, "y": 100},
            "B5": {"x": 631, "y": 100},
            "C1": {"x": 0, "y": 200},
            "C2": {"x": 140, "y": 200},
            "C3": {"x": 290, "y": 200},
            "C4": {"x": 491, "y": 200},
            "C5": {"x": 631, "y": 200}
        },

        "pipette_model": "foreach",
        "gripper_model": "flexrobo",

        "usb_sn_xy_platform": "10011005AF6998A25E3FEE3AF50020C7",
        "usb_sn_z_platform": "",
        "usb_sn_pipette": "8C9CF2DFF27FEA119526CA1A09024092",
        "usb_sn_modbus": "D2B376D8C37FEA11A2BCCA1A09024092"

    }

    deck = Deck(robot_config)
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
    print("current_reactor", current_reactor)
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

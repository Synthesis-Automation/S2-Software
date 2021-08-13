# The deck module gives the cooridinates of all plates and vials placed on the deck
# It also manages robot_config
# It also manages plate definition
# It also manages calibration data

# The internal data structure of deck class, all unit is mm

# Data structure of vial generated from deck.vial(plate="A1", vial="B2"), diameter is for the cap
# {'x': 10, 'y': 10, 'z': 0, 'depth': 40, 'plate': 'A1', 'vial': 'A1', 'type': 'plate_5mL', 'diameter': 18.0}

# self.robot_config

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

class Deck(object):
    def __init__(self, robot_config={}):
        self.robot_config = robot_config
        self.load_robot_config()
        self.load_deck_config()
        self.load_calibration()
        self.setup_plates()

    def load_robot_config(self):
        self.calibration_file = Path(self.robot_config["calibration_file_name"])
        self.deck_config_file = Path(self.robot_config["deck_config_file_name"])
        self.reference = self.robot_config["reference"]
        self._slots = self.robot_config["slots"]
        self.slot_list = self.robot_config["slot_list"]
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
        self.current_tip = self.calibration["current_tip"]
        self.current_tip_small = self.calibration["current_tip_small"]
        self.deck_calibration_x = self.calibration["Z2"][0]-self.reference["x"]
        self.deck_calibration_y = self.calibration["Z2"][1]-self.reference["y"]

    def set_current_tip(self, tip=0, tip_type="tips_1000uL"):
        if tip_type == "tips_1000uL":
            self.current_tip = tip
        elif tip_type == "tips_50uL":
            self.current_tip_small = tip
        else:
            print("Wrong tipe type")

    def get_current_reactor(self):
        '''return something like reactor_square_8mL_20p'''
        return self.current_reactor

    def get_current_reactor_slot(self):
        '''return reactor slot such as R1, R2'''
        reactor_no = self.robot_config["reactor_list"].index(
            self.current_reactor)
        reactor_slot = self.robot_config["reactor_slot_list"][reactor_no]
        return reactor_slot

    def reset_current_reactor(self):
        '''reset value of current reactor from data in plate assignment'''
        reactor_slot = self.get_plate_assignment(assignment="Reactor")
        reactor_name = self.deck_config[reactor_slot]["plate"]
        self.current_reactor = reactor_name.split(':')[0]

    def save_current_tip(self, tip_type="tips_1000uL"):
        if tip_type == "tips_1000uL":
            self.save_calibration("current_tip", self.current_tip)
        elif tip_type == "tips_50uL":
            self.save_calibration("current_tip_small", self.current_tip_small)
        else:
            print("Wrong tipe type")

    def get_current_tip(self, format="number", tip_type="tips_1000uL"):
        '''return numeric format such as 0, 1 when format = number, else return non-numeric format such as A1'''
        if tip_type == "tips_1000uL":
            if format == "number":
                return self.current_tip
            else:
                return self.convert_number_to_A1_by_plate_type(self.current_tip, plate_type="tiprack_1000ul")
        elif tip_type == "tips_50uL":
            if format == "number":
                return self.current_tip_small
            else:
                return self.convert_number_to_A1_by_plate_type(self.current_tip_small, plate_type="tiprack_1000ul")
        else:
            print("Wrong tipe type")

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
        from chem_robox.tools import helper
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
        from chem_robox.tools import helper
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
                    'chem_robox/config/plate_definition')
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

    def get_plate_type_of_slot(self, slot="A1"):
        '''get plate_type_of_slot (e.g., slot = A1)'''
        plate_name = self.deck_config[slot]["plate"]
        plate_type = plate_name.split(':')[0]
        return plate_type

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
            'chem_robox/config/plate_definition')
            / (plate_type + ".json"))
        return plate_definition['ordering']

    def get_cols_rows_by_plate_type(self, plate_type="plate_2mL"):
        # generate the vial cols_rows e.g., {"columns": 5, "rows": 6}
        plate_definition = self.read_plate_definition(Path(
            'chem_robox/config/plate_definition')
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

# example of self.deck_config
# {
#     "A1": {"plate": "plate_5mL:001", "assignment": "Reagent"},
#     "A2": {"plate": "plate_5mL:001", "assignment": "Reagent"},


    def get_plate_list(self):
        self.plate_list = []
        for slot in self.deck_config:
            self.plate_list.append(self.deck_config[slot]["plate"])
        return self.plate_list
            
    def is_plate_on_deck(self, plate_list):
        unassigned_plate = []
        self.get_plate_list()
        for plate_name in plate_list:
            if plate_name not in self.plate_list:
                unassigned_plate.append(plate_name)
        return unassigned_plate


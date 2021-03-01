import json
from pathlib import Path


class Slot(object):
    def __init__(self, robot_rows = 3, robot_cols = 5):
        self.robot_rows = robot_rows
        self.robot_cols = robot_cols
        self.robot_config_file = Path("combinewave/config/robot_config.json")
        self.load_robot_config()
        self.setup_slot_on_deck()

    def load_robot_config(self):
        with open(self.robot_config_file) as config:
            self.robot_config = json.load(config)

    def get_slot_offsets(self):
        return (self.robot_config['row_offset'],
                self.robot_config['col_offset'])

    def get_max_robot_rows(self):
        return self.robot_config['max_robot_rows']

    def get_max_robot_cols(self):
        return self.robot_config['max_robot_cols']

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

    def save_calibration(self, plate, calibration_data):
        '''save calibration data for one plate in the slot '''
        # example: 'plate='A1', calibration_data=[1, 20, 10.50]'
        self.calibration[plate] = calibration_data
        with open(self.calibration_file, "w") as json_file:
            json.dump(self.calibration, json_file)
        from combinewave.tools import helper
        helper.format_json_file(self.calibration_file)
        self.update_head_offsets()

    def setup_slot_on_deck(self):
        '''generate coordinates for the upper conner of each slots on the deck as a python dictionary: {"A1": (0, 0, 0)}'''
        self._slots = {}
        robot_cols = self.get_max_robot_cols()
        robot_rows = self.get_max_robot_rows()
        row_offset, col_offset = self.get_slot_offsets()
        A = ord("A")
        row_names = ""
        for i in range(robot_rows):
            row_names = row_names+chr(A+i)
        for row_index, row in enumerate(row_names):
            for col_index, col in enumerate(range(1, robot_cols + 1)):
                slot_coordinates = {
                    "x": (col_offset * col_index),
                    "y": (row_offset * row_index)
                }
                slot_name = "{}{}".format(row, col)
                self._slots.update({slot_name: slot_coordinates})


# test code for this module
if __name__ == '__main__':
    slot = Slot()
    # deck.update_deck_config(deck_config)

    print(slot._slots)
    print()

import json
import os
from pathlib import Path

# This module generate plate definition as a json file.
# An example:
# {
#     "version": 1.0,
#     "name": "plate_40mL",
#     "cornerOffsetFromSlot": {
#         "x": 10,
#         "y": 10,
#         "z": 0
#     },
#     "columns": 3,
#     "rows": 3,
#     "wells": {
#         "A1": {
#             "depth": 30,
#             "volume": 4000,
#             "shape": "circular",
#             "diameter": 13.7,
#             "x": 10,
#             "y": 10,
#             "z": 0
#         },
#         "B1": {
#             "depth": 30,
#             "volume": 4000,
#             "shape": "circular",
#             "diameter": 13.7,
#             "x": 10,
#             "y": 51,
#             "z": 0
#         },


class Plate(object):
    def __init__(self, name='plate_name', grid=(1, 1), spacing=(0, 0), offset=(0, 0), diameter=0, depth=0, height=0, volume=0):
        self.name = name
        self.columns, self.rows = grid
        self.col_spacing, self.row_spacing = spacing
        self.col_offset, self.row_offset = offset
        self.diameter = diameter
        self.volume = volume
        self.depth = depth
        self.height = height

    def creat_plate(self):
        self._wells = {}
        for i in range(self.columns):
            for j in range(self.rows):
                well_name = chr(j + ord('A')) + str(1 + i)
                coordinates = (i * self.col_spacing + self.col_offset,
                               j * self.row_spacing + self.row_offset, 0)
                well = {well_name:
                        {
                            "depth": self.depth,
                            "height": self.height,
                            "volume": self.volume,
                            "shape": "circular",
                            "diameter": self.diameter,
                            "x": coordinates[0],
                            "y": coordinates[1],
                            "z": coordinates[2]
                        }
                        }
                self._wells.update(well)

        vial_list = []
        for i in range(self.columns):
            for j in range(self.rows):
                vial_name = chr(j + ord('A')) + str(1 + i)
                vial_list.append(vial_name)

        self.plate_data = {"version": 1.0,
                           "name": self.name,
                           "cornerOffsetFromSlot": {
                               "x": self.col_offset,
                               "y": self.row_offset,
                               "z": 0
                           },
                           "columns": self.columns,
                           "rows": self.rows,
                           "ordering": vial_list,
                           "wells": self._wells
                           }

    def save_plate_file(self):
        plate_file_name = Path(
            'chem_robox/config/plate_definition/' + self.name + '.json')
        with open(plate_file_name, "w") as json_file:
            json.dump(self.plate_data, json_file)
        with open(plate_file_name, 'r+') as f:
            old_data = json.load(f)
            f.seek(0)
            f.write(json.dumps(old_data, indent=4))
            f.truncate()


# for 96 well plates such as tip rack:

# tip_rack
# my_plate = plate(name='tiprack_1000ul', grid=(12, 8), offset=(
#     14.3, 11.2), spacing=(9, 9), diameter=4.20, depth=0, volume=0)

# plate_5mL
# plate(name='plate_5mL', grid=(8, 5), offset=(
#         10, 10), spacing=(15.5, 16.7), diameter=10, depth=0, volume=0)
#     my_plate.creat_plate()

# plate_40mL
# my_plate = plate(name='plate_40mL', grid=(3, 2), offset=(
#         10, 10), spacing=(43.6, 43.6), diameter=13.7, depth=0, volume=0)
#     my_plate.creat_plate()

if __name__ == "__main__":
    # my_plate = Plate(name='plate_40mL', grid=(column, row), offset=(
    #         10, 10), spacing=(42.8, 42.8), diameter=13.7, depth=0, volume=0)
    # my_plate.creat_plate()
    # my_plate.save_plate_file()

    my_plate = Plate(name='tiprack_1000uL', grid=(12, 8), offset=(
        15.3, 12.2), spacing=(9, 9), diameter=4.20, depth=0, height=10, volume=0)
    my_plate.creat_plate()
    my_plate.save_plate_file()

    my_plate = Plate(name='clean_up', grid=(25, 25), offset=(
        0, 0), spacing=(0.6, 0.6), diameter=4.20, depth=60, height=164, volume=0)
    my_plate.creat_plate()
    my_plate.save_plate_file()

    my_plate = Plate(name='tiprack_50uL', grid=(12, 8), offset=(
        15.3, 12.2), spacing=(9, 9), diameter=4.20, depth=0, height=10, volume=0)
    my_plate.creat_plate()
    my_plate.save_plate_file()

    my_plate = Plate(name='plate_2mL', grid=(8, 5), offset=(
        9.55, 10.7), spacing=(15.5, 16), diameter=11.7, depth=31, height=180, volume=1500)
    my_plate.creat_plate()
    my_plate.save_plate_file()

    my_plate = Plate(name='plate_50mL', grid=(3, 2), offset=(
        22.8, 22.2), spacing=(41, 41), diameter=13.7, depth=89.0, height=178, volume=4000)
    my_plate.creat_plate()
    my_plate.save_plate_file()

    my_plate = Plate(name='plate_15mL', grid=(4, 3), offset=(
        23, 19), spacing=(27, 24.5), diameter=18.0, depth=72, height=103, volume=4000)
    my_plate.creat_plate()
    my_plate.save_plate_file()

    my_plate = Plate(name='plate_5mL', grid=(7, 4), offset=(
        9.8, 9.7), spacing=(18.0, 22), diameter=18.0, depth=82, height=172, volume=4000)
    my_plate.creat_plate()
    my_plate.save_plate_file()

    my_plate = Plate(name='workup_small', grid=(4, 3), offset=(
        10, 10), spacing=(30.5, 28.5), diameter=21.0, depth=50.0, height=175.0, volume=4000)
    my_plate.creat_plate()
    my_plate.save_plate_file()

    my_plate = Plate(name='workup_big', grid=(3, 2), offset=(
        10, 10), spacing=(134, 92), diameter=18.0, depth=82.7, height=105.7, volume=4000)
    my_plate.creat_plate()
    my_plate.save_plate_file()

    my_plate = Plate(name='reactor_12p', grid=(4, 3), offset=(
        43.75, 56.62), spacing=(24.0, 24.5), diameter=18.0, depth=58, height=168, volume=8000)
    my_plate.creat_plate()
    my_plate.save_plate_file()

    my_plate = Plate(name='deck', grid=(5, 3), offset=(
        23, 16.5), spacing=(27, 27), diameter=18.0, depth=59, height=107.5, volume=4000)
    my_plate.creat_plate()
    my_plate.save_plate_file()

    my_plate = Plate(name='plate_10mL', grid=(4, 3), offset=(
        15.8, 14.7), spacing=(32.0, 28), diameter=18.0, depth=50, height=148, volume=10000)
    my_plate.creat_plate()
    my_plate.save_plate_file()

    my_plate = Plate(name='plate_10mL_old', grid=(4, 3), offset=(
        15.8, 14.7), spacing=(32.0, 28), diameter=18.0, depth=52, height=156, volume=10000)
    my_plate.creat_plate()
    my_plate.save_plate_file()
import json
import os
from pathlib import Path
import math

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


class Plate_rect(object):
    def __init__(self, name='plate_name', grid=(1, 1), spacing=(0, 0), offset=(0, 0), column_offset_2=0, diameter=0, depth=0, height=0, volume=0):
        self.name = name
        self.columns, self.rows = grid
        self.col_spacing, self.row_spacing = spacing
        self.col_offset, self.row_offset = offset
        self.diameter = diameter
        self.volume = volume
        self.depth = depth
        self.height = height
        self.column_offset_2 = column_offset_2

    def creat_plate(self):
        self._wells = {}
        for i in range(self.columns):
            for j in range(self.rows):
                well_name = chr(j + ord('A')) + str(1 + i)
                if j % 2 == 0:  # j is even
                    coordinates = (i * self.col_spacing + self.col_offset,
                                   j * self.row_spacing + self.row_offset, 0)
                else:
                    coordinates = (i * self.col_spacing + self.column_offset_2,
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
        for i in range(self.rows):
            for j in range(self.columns):
                vial_name = chr(i + ord('A')) + str(1 + j)
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


class Plate_circle(object):
    def __init__(self, name='plate_name', letter="A", reactors=18, starting_angle=math.pi/36, radius=135/2, radius_2=0, offset=(0, 0), diameter=0, depth=0, height=0, volume=0):
        self.name = name
        self.columns, self.rows = (2, 18)
        self.col_offset, self.row_offset = offset
        self.diameter = diameter
        self.volume = volume
        self.depth = depth
        self.height = height
        self.reactors = reactors
        self.angle = math.pi*2/reactors
        self.starting_angle = starting_angle
        self.radius = radius
        self.letter = letter
        self.radius_2 = radius_2

    def creat_plate(self):
        self._wells = {}
        ordering = []
        for i in range(self.reactors):
            well_name = self.letter + str(1 + i)
            my_angle = self.angle*i+self.starting_angle
            print(my_angle)
            x = self.radius + round(math.sin(my_angle)*self.radius, 2)
            y = self.radius - round(math.cos(my_angle)*self.radius, 2)
            well = {well_name:
                    {
                        "depth": self.depth,
                        "height": self.height,
                        "volume": self.volume,
                        "shape": "circular",
                        "diameter": self.diameter,
                        "x": x,
                        "y": y,
                        "z": 0
                    }
                    }
            print(i, well)
            ordering.append(well_name)
            self._wells.update(well)

        # second circle
        if self.radius_2 > 0:
            for j in range(2):
                well_name = self.letter + str(self.reactors + j+1)
                if j == 0:
                    x = self.radius_2*-1
                else:
                    x = self.radius_2
                y = 0
                well = {well_name:
                        {
                            "depth": self.depth,
                            "height": self.height,
                            "volume": self.volume,
                            "shape": "circular",
                            "diameter": self.diameter,
                            "x": x,
                            "y": y,
                            "z": 0
                        }
                        }
                print(i, well)
                ordering.append(well_name)
                self._wells.update(well)

        self.plate_data = {"version": 1.0,
                           "name": self.name,
                           "cornerOffsetFromSlot": {
                               "x": self.col_offset,
                               "y": self.row_offset,
                               "z": 0
                           },
                           "ordering": ordering,
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


if __name__ == "__main__":
    my_plate = Plate_rect(name='caps', grid=(5, 4), offset=(
        23.55, 12.82), column_offset_2=12.05, spacing=(23.0, 19.92), diameter=18.0, depth=59.0, height=155.0, volume=0)
    my_plate.creat_plate()
    my_plate.save_plate_file()

    # my_plate = Plate_rect(name='caps', grid=(5, 4), offset=(
    #     12.05, 12.82), column_offset_2=23.55, spacing=(23.0, 19.92), diameter=18.0, depth=59.0, height=156.0, volume=0)
    # my_plate.creat_plate()
    # my_plate.save_plate_file()

    my_plate = Plate_rect(name='reactor_square_8mL_20p', grid=(5, 4), offset=(
        23.55, 12.82), column_offset_2=12.05, spacing=(23.0, 19.92), diameter=18.0, depth=59.0, height=166.0, volume=0)
    my_plate.creat_plate()
    my_plate.save_plate_file()

    my_plate = Plate_rect(name='workup_8mL_20p', grid=(5, 4), offset=(
        23.55, 12.82), column_offset_2=12.05, spacing=(23.0, 19.92), diameter=18.0, depth=59.0, height=139.0, volume=0)
    my_plate.creat_plate()
    my_plate.save_plate_file()

    my_plate = Plate_rect(name='plate_GC_LC_2mL', grid=(5, 4), offset=(
        17.8, 12.822), column_offset_2=17.8, spacing=(23.0, 19.918), diameter=18.0, depth=59.0, height=186.5, volume=0)
    my_plate.creat_plate()
    my_plate.save_plate_file()

    my_plate = Plate_circle(name='reactor_circle_8mL_20p', letter="A", reactors=18, starting_angle=math.pi/18,
                            radius=135/2, radius_2=11.4, offset=(0, 0), diameter=0, depth=59, height=144, volume=0)
    my_plate.creat_plate()
    my_plate.save_plate_file()

    my_plate = Plate_circle(name='reactor_circle_8mL_10p', letter="A", reactors=10, starting_angle=math.pi /
                            10, radius=76/2, offset=(0, 0), diameter=0, depth=59, height=175, volume=0)
    my_plate.creat_plate()
    my_plate.save_plate_file()



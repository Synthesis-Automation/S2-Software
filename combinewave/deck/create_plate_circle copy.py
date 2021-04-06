import json
import os, math
from pathlib import Path

class Plate(object):
    def __init__(self, name='plate_name', letter = "A", reactors = 16, radius = 144, offset=(0, 0), diameter=0, depth=0, height=0, volume=0):
        self.name = name
        self.columns, self.rows = (3, 16)
        self.col_offset, self.row_offset = offset
        self.diameter = diameter
        self.volume = volume
        self.depth = depth
        self.height = height
        self.reactors = reactors
        self.angle = math.pi*2/reactors
        self.radius = radius
        self.letter = letter

    def creat_plate(self):
        self._wells = {}
        ordering = []
        for i in range(self.reactors):
            well_name = self.letter + str(1 + i)
            x = round(math.cos(math.pi/2-self.angle*i)*self.radius, 2)
            y = round(math.sin(math.pi/2-self.angle*i)*self.radius, 2)
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
            'combinewave/config/plate_definition/' + self.name + '.json')
        with open(plate_file_name, "w") as json_file:
            json.dump(self.plate_data, json_file)
        with open(plate_file_name, 'r+') as f:
            old_data = json.load(f)
            f.seek(0)
            f.write(json.dumps(old_data, indent=4))
            f.truncate()



if __name__ == "__main__":

    my_plate = Plate(name='reactor_27-1', letter = "A", reactors = 16, radius = 144, offset=(0, 0), diameter=18.0, depth=58, height=162, volume=8000)
    my_plate.creat_plate()
    my_plate.save_plate_file()

    my_plate = Plate(name='reactor_27-2', letter = "B", reactors = 10, radius = 90, offset=(0, 0), diameter=18.0, depth=58, height=162, volume=8000)
    my_plate.creat_plate()
    my_plate.save_plate_file()

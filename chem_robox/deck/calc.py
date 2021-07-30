import json
import os
import math
from pathlib import Path


def read_plate_definition(plate_definition_file=r'..\config\plate_definition\plate_GC_LC_2mL.json'):
    with open(plate_definition_file) as data:
        plate = json.load(data)
    return plate

plate = read_plate_definition()
# print(plate["wells"])
# print(plate["ordering"])


item_list = []
number_of_reactor = len(plate["ordering"])


# cyclic
print("\n")
# MAX = 170
# for i in range(number_of_reactor):
#     name = plate["ordering"][i]
#     x = plate["wells"][name]["x"]/MAX+0.3
#     y = plate["wells"][name]["y"]/MAX+0.2
#     item_list.append({"name": name, "x": x, "y": y})


# cyclic
MAX = 140
for i in range(number_of_reactor):
    name = plate["ordering"][i]
    x = plate["wells"][name]["x"]/MAX
    y = plate["wells"][name]["y"]/MAX+0.2
    item_list.append({"name": name, "x": x, "y": y})




print(item_list)

print("\n")


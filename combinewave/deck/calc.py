import json
import os
import math
from pathlib import Path


def read_plate_definition(plate_definition_file=r'..\config\plate_definition\reactor_27p copy.json'):
    with open(plate_definition_file) as data:
        plate = json.load(data)
    return plate


plate = read_plate_definition()
# print(plate["wells"])
# print(plate["ordering"])

item_list = [
    {"name": "A1", "x": 0.1, "y": 0.1},
    {"name": "B1", "x": 0.2, "y": 0.2},
    {"name": "C1", "x": 0.9, "y": 0.9}
]

item_list = []

MAX = 180
for i in range(27):
    name = plate["ordering"][i]
    x = 0.5 + plate["wells"][name]["x"]/MAX/2
    y = 0.5-plate["wells"][name]["y"]/MAX/2
    item_list.append({"name": name, "x": x, "y": y})

for i in range(27):
    name = plate["ordering"][i]
    x = plate["wells"][name]["x"]/2
    y = plate["wells"][name]["y"]/2
    plate["wells"][name]["x"] = 80 + x
    plate["wells"][name]["y"] = 80 - y

# print(item_list)

print()

print(plate["wells"])

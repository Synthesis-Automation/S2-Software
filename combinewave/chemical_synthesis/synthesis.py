# Chemistry part of the project
# This module is the main entrance for protocol and reagent database managements
# The synthesis module parses the synthesis plan
# It also manages reagent database

# The parseed synthesis plan data was saved to self.synthesis_plan_json
# The required_plates was saved to self.required_plate

# The internal data structure of deck class

# self.reagent_index, as a list
# example:
# [['THF', cas-no, 'plate_40mL:001', 'A1', 'pure_liquid', 0.0], ['Toluene', nan, 'plate_40mL:001', 'A2', 'pure_liquid', 0.0]]

# self.synthesis_plan_json
# the parsed reaction plan as a json file
# example:
# [
#     {
#         "tracking_number": "12/24/2020/21:32-RXN-1",
#         "reactor_no": 1,
#         "addition_temperature": 25.0,
#         "reaction_time": 6.0,
#         "reaction_temperature": 25.0,
#         "reagents": [
#             {
#                 "name": "1-Octene",
#                 "type": "pure_liquid",
#                 "plate": "plate_5mL:001",
#                 "position": "C1",
#                 "amount": 0.0314
#             },
#             {
#                 "name": "DCM",
#                 "type": "pure_liquid",
#                 "plate": "plate_40mL:001",
#                 "position": "B1",
#                 "amount": 1.5
#             }
#         ]

import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd
import math
from combinewave.tools import helper


class Synthesis(object):
    def __init__(
        self,
        reagent_file="",
        synthesis_plan_file=""
    ):
        self.reagent_file = reagent_file
        self.synthesis_plan_file = synthesis_plan_file
        self.load_reagent_index(self.reagent_file)
        self.synthesis_plan_json = []
        self.ready = False

    def load_reagent_index(self, file_name):
        try:
            data = pd.read_excel(file_name)
            # read reagent index excel file and convert it to a list
            reagents = data.values.tolist()
        except:
            error = sys.exc_info()[0]
            print("Error reading reagent_index:", error)
        self.reagent_index = []
        # remove entry with empty name
        for entry in reagents:
            if str(entry[0]).strip() != 'nan' and str(entry[0]).strip() != '':
                self.reagent_index.append(entry)

    def load_synthesis_plan(self, file_name):
        try:
            self.synthesis_plan = []
            with open(file_name) as csvFile:
                csv_Reader = csv.reader(csvFile, delimiter=';')
                for row in csv_Reader:
                    space_striped_row = [x.strip(" ") for x in row]
                    # strip the spaces at begining of each word lstrip or strip
                    # ignore empty line, line start with '#', and any line do not contain '('
                    if space_striped_row == [] or space_striped_row[0] == "":
                        continue
                    if not '(' in space_striped_row[0]:
                        continue
                    if '#' in space_striped_row[0]:
                        continue
                    # remove '(' and ')' ','
                    cleaned_row = [re.sub("[(),]", " ", x)
                                   for x in space_striped_row]
                    self.synthesis_plan.append(cleaned_row)
            csvFile.close()
        except:
            error = sys.exc_info()[0]
            print("Error reading synthesis_plan_file:", error)
        return self.parse_plan_to_json()

    def load_synthesis_plan_excel(self, file_name):
        try:
            plan_data_frame = pd.read_excel(file_name).fillna(value=" ") #drop row with nan
            # read reagent index excel file and convert it to a list
            plan_data = plan_data_frame.values.tolist()
        except:
            error = sys.exc_info()[0]
            print("Error reading plan excel file:", error)
        self.synthesis_plan = []
        for row in plan_data:
            if not row[0]:
                continue
            # strip '( ) ,'
            cleaned_row = [re.sub("[(),]", " ", x) for x in row]
            # strip the spaces at begining of each word lstrip or strip
            row_no_space = [x.strip(" ") for x in cleaned_row]
            self.synthesis_plan.append(row_no_space)
        return self.parse_plan_to_json()

    def load_synthesis_plan_from_string(self, txt):
        self.synthesis_plan = []
        lines = txt.splitlines()
        for row in csv.reader(lines, delimiter=';'):
            space_striped_row = [x.strip(" ") for x in row]
            # strip the spaces at begining of each word lstrip or strip
            # ignore empty line, line start with '#', and any line do not contain '('
            if space_striped_row == [] or space_striped_row[0] == "":
                continue
            if not '(' in space_striped_row[0]:
                continue
            if '#' in space_striped_row[0]:
                continue
            # remove '(' and ')'
            cleaned_row = [re.sub("[(),]", " ", x)
                           for x in space_striped_row]
            self.synthesis_plan.append(cleaned_row)
        # print(self.synthesis_plan)
        return self.parse_plan_to_json()

    def locate_reagent(self, reagent_name):  # A position is like A1, B4
        # Note: The first column is reagent name; 2nd: plate name; 3rd: location (A1, B2 ect); 4th: amount in mmol, 0 , indicate it is a solvent or liquid.
        reagent_found = False
        reagent_name_lower_case = reagent_name.lower()  # the program ignores the case
        NAME_ROW = 0
        CAS_ROW = 1
        PLATE_ROW = 2
        VIAL_ROW = 3
        TYPE_ROW  = 4
        AMOUNT_ROW = 5
        for row in range(len(self.reagent_index)):
            name = self.reagent_index[row][NAME_ROW].strip()  # extract the first word
            name_lower_case = name.lower()
            if reagent_name_lower_case == name_lower_case:
                my_reagent_plate = self.reagent_index[row][PLATE_ROW].strip()
                my_reagent_vial = self.reagent_index[row][VIAL_ROW].strip()
                my_reagent_type = self.reagent_index[row][TYPE_ROW].strip()
                my_reagent_amount = self.reagent_index[row][AMOUNT_ROW]
                reagent_found = True
        if reagent_found == False:
            print(reagent_name, "was not in the reagent list")
            return reagent_name+" was not found in the reagent databse.\nPlease edit your reagent_index (excel file)."
        return {'plate': my_reagent_plate, 'vial': my_reagent_vial, 'type': my_reagent_type, 'amount': my_reagent_amount}

    def parse_plan_to_json(self):
        rxn_data = []
        self.reagent_plate_list = []
        reaction_no = 1
        for row in self.synthesis_plan:  # each row is the data for one reaction
            addition_temperature = None
            reaction_time = None
            reaction_temperature = None
            workup_entry = None    
            reagents = []
            for i in range(len(row)):
                # $ for user defined regent, the progrem ignore any entry contain $
                if '$' in row[i]:
                    continue

                if "Addition-temperature" in row[i]:
                    addition_temperature = helper.get_float_number(row[i])
                    continue

                if "Reaction-temperature" in row[i]:
                    reaction_temperature = helper.get_float_number(row[i])
                    continue

                if "Reaction-time" in row[i]:
                    reaction_time = helper.get_float_number(row[i])
                    continue

                if "Workup" in row[i]:
                    if 'none' in row[i]:
                        workup_entry = {}
                    else:
                        workup_solution = row[i].split()[1]
                        workup_volume = helper.get_float_number(row[i])
                        workup_reagent = self.locate_reagent(workup_solution)
                        if "not found" in workup_reagent:
                            return workup_reagent
                        workup_entry = {
                            "name": workup_solution,
                            "type": workup_reagent['type'],
                            "plate": workup_reagent['plate'],
                            "position": workup_reagent['vial'],
                            "amount": workup_volume
                        }
                    continue

                if "mL" in row[i]:
                    # split to find the first word
                    liquid_name = row[i].split(None, 1)[0]
                    liquid_volume = helper.get_float_number(row[i])
                    liquid = self.locate_reagent(liquid_name)
                    if "not found" in liquid:
                        return liquid
                    reagents.append(
                        {
                            "name": liquid_name,
                            "type": liquid['type'],
                            "plate": liquid['plate'],
                            "position": liquid['vial'],
                            "amount": liquid_volume
                        }
                    )
                    self.reagent_plate_list.append(liquid['plate'])
                    continue

                if "mmol" in row[i]:
                    tablet_name = row[i].split(None, 1)[0]
                    tablet_amount = helper.get_float_number(row[i])

                    tablet = self.locate_reagent(tablet_name)
                    if "not found" in tablet:
                        return tablet
                    number_of_tablet = int(
                        math.ceil(tablet_amount/float(tablet['amount'])))
                    reagents.append(
                        {
                            "name": tablet_name,
                            "type": tablet['type'],
                            "plate": tablet['plate'],
                            "position": tablet['vial'],
                            "amount": number_of_tablet
                        }
                    )
                    self.reagent_plate_list.append(tablet['plate'])
                    continue
            now = datetime.now()
            # dd/mm/YY H:M:S
            if not addition_temperature:
                addition_temperature = 25
            if not reaction_time:
                reaction_time = 1
            if not reaction_temperature:
                reaction_temperature = 25
            if not workup_entry:
                workup_entry = {"name": "None"}

            time_stamp = now.strftime("%m/%d/%Y/%H:%M")
            json_entry = {
                "tracking_number": time_stamp + "-RXN-" + str(reaction_no),
                "reactor_no": reaction_no,
                "addition_temperature": addition_temperature,
                "reaction_time": reaction_time,
                "reaction_temperature": reaction_temperature,
                "reagents": reagents,
                "workup": workup_entry
                }
            rxn_data.append(json_entry)
            reaction_no += 1
            addition_temperature = None
            reaction_time = None
            reaction_temperature = None
            workup_entry = None

        with open(Path("user_files/reactions.json"), "w") as json_file:
            json.dump(rxn_data, json_file)
        self.synthesis_plan_json = rxn_data
        helper.format_json_file(Path("user_files/reactions.json"))
        self.plate_list = self.get_required_reagent_plate()
        return "success"

    def save_plan(self, save_file=Path("user_files/Conducted_reactions.txt"), reactor_starting_nubmer=0):
        reaction_no = reactor_starting_nubmer
        with open(save_file, 'w') as output:
            filename = '\nProtocol file name:  ' + save_file + '\nRequired plates:  '
            output.write(filename)
            plates = ', '.join(self.get_required_reagent_plate())+'\n'
            output.write(plates)
            for row in self.synthesis_plan:
                new = row  # each row is the data for one reaction
                # first 5 letter of file name + reactor no
                new.insert(0, 'Reactor No. '+str(reaction_no))
                output.write(str(new) + '\n')
                reaction_no = reaction_no+1
            # output.write('\n')

    def get_required_reagent_plate(self):
        # remove duplicate plates
        self.required_plate = list(set(self.reagent_plate_list))
        return self.required_plate

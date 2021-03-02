# Open Automated Chemical Synthesis Platform (model S2)

- [Overview](#overview)
- [S2 API](#S2-api)
- [S2 App](#S2-app)
- [Contributing]

## Overview

Wellcome to Open Automated Chemical Synthesis Platform (model S2) 

Our mission is to provide a simple platform for synthetic chemists to share chemical synthesis protocols and replicate each other's work. Our robots can automate experiments that could have been done manually. We also want to build a stardard hardware interface to make introduction of new hardware modules easier.

This repository contains the source code for the S2 API and also GUI app.

## S2 API

1) Robot (robot.py)
Main function: the only entrance for hardware control
Hardware drivers:
	- XY_platform (using smoothieware, USB)
	- Z_platform (using arduino, USB)
	- E-Pipette (for liquid handling, commericial - Hamilton, RS232)
	- Gripper (for cap handling, commerical, RS485 modbus)
	- Communication (USB to RS232， USB to RS485)
Based these drivers
	- Liquid handler
	- Tablet handler
	- Capper handler
	was builded.
2) Deck (deck.py, create_plate.py)
Main function: Convert user vial/bottle locator (plate, vial) such as ("A1", "B2") to phisical coordinate such as {'x': 0, 'y':10, 'z': 10.3})
	- The deck module gives the cooridinates of all plates and vials placed in the deck
	- It also manages robot config and deck configuration
	- It also create and manages plate definition
	- It also manages calibration data and head offsets

3) Chemical synthesis (synthesis.py)
Function: The chemistry part of project
	- Reagent database management
		- Regent index (using excel file, may use SQL in the future)
	- Reaction protocol management
		- Reaction plan reading (using a txt/csv file, may use a GUI)
		- Convert to a JSON file for execution.
	- Bio modules (for future)

API Interface:
Examples:
	robot.connect()
	robot.pickup_tip()
	robot.transfer_liquid(from = vial1, to = vial2, volume = 100, tip = tip1)
	robot.decap (vial)
	synthesis.load_reagent_index(file)
	synthesis.parse_plan_to_json()

## S2 GUI App

	- Tkinter (for now)
	- API calls via robot mudule and chemical synthesis module


Easily upload a protocol, calibrate positions, and run your experiment from your computer.

This program used many open-source hardware and software projects:
e.g., Arduino, AccelStepper, smoothieware for hardware controls; Opentrons, numpy, pandas in software part
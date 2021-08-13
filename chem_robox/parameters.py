# defintions of constants used in program
LARGE_FONT = ("Verdana", 11)
NORMAL_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 9)

steps_per_mm_Z = 64      # 8 mm, 2 microstepping: 2x200/8 = 50 for makerbase 

LIQUID = "Z1"
TABLET = "Z2"
CAPPER = "Z3"

GRIPPER_ID = 1
Z_NORMAL_SPEED = 3000


VERSION = "v 1.0"
SYSTEM_NAME = "Open Automatic Chemical Synthesis Platform - ChemRobox"
NEW_PLAN_HEADER = "# No space in names, ',' as seperator, 'mL' for liquids, 'mmol' for solids, program ignores chemical name start with '$'. \n\nCompound_A (0.005 mmol), Solvent_B (2 mL), Reaction-temperature (25.0 degree), Reaction-time (6.0 h)"

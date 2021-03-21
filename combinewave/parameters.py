# defintions of constants used in program

LARGE_FONT = ("Verdana", 11)
NORMAL_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 9)

steps_per_mm_Z = 100      # 4 mm, 2 microstepping: 2x200/4

CAPPER = "Z1"
TABLET = "Z2"
LIQUID = "Z3"
GRIPPER_ID = 1

VERSION = "v1.5"
SYSTEM_NAME = "Open Automatic Chemical Synthesis Platform"
NEW_PLAN_HEADER = "# Note: No space in names, ';' to seperate each item, 'mL' for liquid chemicals, 'mmol' for solid chemicals, program ignores any chemical name start with '$'.\n# Example: \n\nCompound_A (0.005 mmol); Solvent_B (2 mL); Reaction-temperature (25.0 degree); Reaction-time (6.0 h)."

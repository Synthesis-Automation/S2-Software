import sys
from combinewave.robot.drivers.xy_platform import xy_platform
from combinewave.deck import deck

deck_config = {"A1": "plate_5mL:001", "A2": "plate_5mL:002", "A3": "plate_5mL:003", "A4": "plate_40mL:001", "A5": "not_used:001", "B1": "plate_5mL:003", "B2": "plate_5mL:004",
               "B3": "tiprack_1000ul:002", "B4": "trash:001", "B5": "plate_15mL:001", "C1": "plate_5mL:005", "C2": "plate_5mL:006", "C3": "tiprack_1000ul:001", "C4": "not_used:001", "C5": "not_used:001"}
deck = deck.Deck(deck_config)

USB_port = 'com5'
xy_platform = xy_platform.XY_platform(
    port=USB_port, head_offsets=deck.head_offsets, calibration=deck.calibration)
xy_platform.connect()
a = xy_platform.smoothie.get_firmware_version()
print(a)

xy_platform.home(axe='xy')

xy_platform.smoothie.set_steps_per_mm('x', 320)
xy_platform.smoothie.set_steps_per_mm('y', 320)

xy_platform.set_acceleration(x=600, y=600)  # default 1200 mm/sec2
xy_platform.set_speed(x=8000, y=8000)


xy_platform.move(x=200,  y=300)

# # speed test
# for i in range(1):
#     xy_platform.move(x=500,  y=300)
#     xy_platform.move(x=-500, y=-300)
# print(xy_platform.smoothie.speeds)
# print(xy_platform.smoothie.get_steps_per_mm('x'))
# print(xy_platform.smoothie.get_steps_per_mm('y'))


vial_1 = deck.vial(plate='A1', vial='A1')
print(vial_1)
vial_2 = deck.vial(plate='C5', vial='A1')
print(vial_2)
for i in range(10):
    xy_platform.move_to(vial=vial_1)
    xy_platform.move_to(vial=vial_2)
print('Done')

# import time
# index = 3
# for i in range(10):
# 	xy_platform.mosfet_engage(index)   # 2 is for the fan (top one)
# 	time.sleep(0.5)
# 	xy_platform.mosfet_disengage(index)
# 	time.sleep(0.5)

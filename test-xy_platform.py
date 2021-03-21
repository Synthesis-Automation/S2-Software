import sys
from combinewave.robot.drivers.xy_platform import xy_platform
from combinewave.deck import deck

USB_port = 'com5'
xy_platform = xy_platform.XY_platform(port=USB_port)
xy_platform.connect()
i=0
for i in range(1000):
    a = xy_platform.smoothie.get_firmware_version()
    print(i, a)

# xy_platform.home(axe='xy')

# xy_platform.smoothie.set_steps_per_mm('x', 320)
# xy_platform.smoothie.set_steps_per_mm('y', 320)

# xy_platform.set_acceleration(x=600, y=600)  # default 1200 mm/sec2
# xy_platform.set_speed(x=8000, y=8000)


# xy_platform.move(x=200,  y=300)

# # # speed test
# # for i in range(1):
# #     xy_platform.move(x=500,  y=300)
# #     xy_platform.move(x=-500, y=-300)
# # print(xy_platform.smoothie.speeds)
# # print(xy_platform.smoothie.get_steps_per_mm('x'))
# # print(xy_platform.smoothie.get_steps_per_mm('y'))


# vial_1 = deck.vial(plate='A1', vial='A1')
# print(vial_1)
# vial_2 = deck.vial(plate='C5', vial='A1')
# print(vial_2)
# for i in range(10):
#     xy_platform.move_to(vial=vial_1)
#     xy_platform.move_to(vial=vial_2)
# print('Done')

# # import time
# # index = 3
# # for i in range(10):
# # 	xy_platform.mosfet_engage(index)   # 2 is for the fan (top one)
# # 	time.sleep(0.5)
# # 	xy_platform.mosfet_disengage(index)
# # 	time.sleep(0.5)

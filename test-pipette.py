from chem_robox.robot.drivers.pipette import pipette_foreach
from chem_robox.robot.drivers.serial_connection import get_port_by_VID_list, get_port_by_serial_no
from pathlib import Path
import json
from chem_robox.deck import deck

robot_config_file = Path("chem_robox/config/robot_config.json")
with open(robot_config_file) as config:
    robot_config = json.load(config)
my_deck = deck.Deck(robot_config)

# Convert a string to a hex nmuber (VID)
usb_vid_pipette = robot_config["usb_serial_VID"]["pipette"]
pipette_port = get_port_by_VID_list(usb_vid_pipette)

pipette = pipette_foreach.Pipette(pipette_port)
pipette.connect()
pipette.initialization()
pipette.increase_range()
# pipette.send_pickup_tip_cmd()

# res = pipette.is_tip_attached()
# # input("wait for tip")
# # res = pipette.is_tip_attached()
# pipette.set_speed(15)
# pipette.aspirate(volume=1000)
# pipette.dispense()


# pipette.aspirate(volume=110)
# pipette.dispense()


for i in range(30):
    print("Start testing...")
    pipette.initialization()
    res = pipette.is_tip_attached()
    pipette.aspirate(i*30)
    res = pipette.is_tip_attached()
    pipette.dispense()
    pipette.send_drop_tip_cmd()
    print(i)


# for i in range(2000):
#     res = pipette.wait_for_finish()
#     print(i)

# input("wait.")
# pipette.set_transport_air_volume(50)
# input("will dispense")
# pipette.dispense()

# input("it will eject tip")
# pipette.send_drop_tip_cmd()
# res = pipette.is_tip_attached()
# print(res)

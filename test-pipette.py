from combinewave import parameters
from combinewave.robot.drivers.pipette import pipette_foreach
import time
pipette = pipette_foreach.Pipette('com4')
pipette.connect()
pipette.initialization()
# pipette.send_pickup_tip_cmd()

# res = pipette.is_tip_attached()
# input("wait for tip")
# res = pipette.is_tip_attached()
# pipette.aspirate(volume=800)

for i in range(2000):
    res = pipette.is_tip_attached()
    pipette.aspirate(150)
    pipette.wait_for_finish()
    res = pipette.is_tip_attached()
    pipette.wait_for_finish()
    pipette.dispense()
    pipette.wait_for_finish()
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

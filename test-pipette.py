from combinewave import parameters
from combinewave.robot.drivers import pipette_foreach
import time
pipette = pipette_foreach.Pipette('com4')
pipette.connect()
pipette.initialization()
# pipette.send_pickup_tip_cmd()

# res = pipette.is_tip_attached()
# input("wait for tip")
# res = pipette.is_tip_attached()

# pipette.aspirate(volume=800)

for i in range(200):
    res = pipette.is_tip_attached()
    pipette.wait_for_finish()
    print(i)

# input("wait.")
# pipette.set_transport_air_volume(50)
# input("will dispense")
# pipette.dispense()


# input("it will eject tip")
# pipette.send_drop_tip_cmd()
# res = pipette.is_tip_attached()
# print(res)

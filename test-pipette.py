from chem_robox.robot.drivers.pipette import pipette_foreach
import time
pipette = pipette_foreach.Pipette('com11')
pipette.connect()
pipette.initialization()
# pipette.increase_range()
# pipette.send_pickup_tip_cmd()

# res = pipette.is_tip_attached()
# # input("wait for tip")
# # res = pipette.is_tip_attached()
# pipette.set_speed(15)
# pipette.aspirate(volume=1000)
# pipette.dispense()


pipette.aspirate(volume=1100)
# pipette.dispense()


# for i in range(100):
#     print("Start testing...")
#     pipette.initialization()
#     res = pipette.is_tip_attached()
#     pipette.aspirate(i*30)
#     res = pipette.is_tip_attached()
#     pipette.dispense()
#     pipette.send_drop_tip_cmd()
#     print(i)


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

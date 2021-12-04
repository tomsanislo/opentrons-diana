from opentrons import protocol_api
# from ot2_helper import OT2Helper
import time

metadata={"apiLevel":"2.5"}

class OT2Helper():

    # defining global variables
    protocol = None

    def __init__(self, protocol):
        self.protocol = protocol

    def blink3(self):
        for i in range(1,4):
            self.protocol.set_rail_lights(False)
            time.sleep(0.7)
            self.protocol.set_rail_lights(True)
            time.sleep(0.7)


    def blink1(self):
        self.protocol.set_rail_lights(False)
        time.sleep(0.7)
        self.protocol.set_rail_lights(True)
        time.sleep(0.7)

    def m_aspirate(self, volume, k, pipette, well):
        base = -2
        pipette.move_to(well.top(z=base))
        if volume < 1400:
            for i in range(1, volume):
                # pipette.aspirate(1, well)
                pipette.move_to(well.top(z=base-i))
                self.protocol.comment(str(i))



def run(protocol: protocol_api.ProtocolContext):
    micronic = protocol.load_labware('micronic_96_tuberack_1400ul', 1)
    falcon = protocol.load_labware("opentrons_6_tuberack_falcon_50ml_conical", 3)
    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 5)
    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tiprack_1])


    helper = OT2Helper(protocol)

    helper.blink3()

    p300.pick_up_tip(tiprack_1["H12"])
    # p300.transfer(1000, falcon["A1"], micronic["H12"])
    # p300.drop_tsip()
    # p300.pick_up_tip()
    # time.sleep(5)
    helper = OT2Helper(protocol)
    # p300.move_to(micronic["H12"].top(z=-42))
    
    helper.m_aspirate(20, 1, p300, micronic.wells_by_name()["H12"])
    protocol.pause()
    # p300.drop_tip()
    p300.drop_tip(tiprack_1["H12"])

    # blinker = OT2Helper(protocol)
    # blinker.blink3()




from opentrons import protocol_api
import json

metadata = {'apiLevel': '2.11'}


def run(protocol: protocol_api.ProtocolContext):
    tiprack = protocol.load_labware("opentrons_96_tiprack_300ul", 5)
    
    pipette = protocol.load_instrument("p300_multi_gen2", "right", tip_racks=[tiprack])

    # p300.pick_up_tip(tiprack_1["H12"])
    
    
    pipette.transfer(100, falcon["A1"], micronic["A1"])
    # p300.aspirate(200, micronic['A1'], rate=2.0)
    # p300.drop_tip() 
    # p300.drop_tsip()
    # p300.pick_up_tip()
    # time.sleep(5)
    # p300.drop_tip()

from opentrons import protocol_api
import json

metadata = {'apiLevel': '2.11'}


def run(protocol: protocol_api.ProtocolContext):
    with open('/data/labware/v2/custom_definitions/micronic_96_tuberack_1400ul.json') as labware_file:
        labware_def = json.load(labware_file)
    micronic = protocol.load_labware_from_definition(labware_def, 1)

    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 5)
    
    p300 = protocol.load_instrument('p300_single', 'left', tip_racks=[tiprack_1])

    # p300.pick_up_tip(tiprack_1["H12"])
    
    
    p300.transfer(100, falcon["A1"], micronic["A1"])
    # p300.aspirate(200, micronic['A1'], rate=2.0)
    # p300.drop_tip() 
    # p300.drop_tsip()
    # p300.pick_up_tip()
    # time.sleep(5)
    # p300.drop_tip()

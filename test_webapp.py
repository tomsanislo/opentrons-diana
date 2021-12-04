from opentrons import protocol_api

metadata = {'apiLevel': '2.11'}

def run(protocol: protocol_api.ProtocolContext):
    # micronic = protocol.load_labware('micronic_96_tuberack_1400ul', 1)
    # falcon = protocol.load_labware("opentrons_6_tuberack_falcon_50ml_conical", 3)
    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 5)
    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tiprack_1])

    p300.pick_up_tip(tiprack_1["H12"])
    
    
    p300.drop_tip(tiprack_1["H12"])

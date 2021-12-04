from opentrons import protocol_api
from helpers import load_config, pick_up_then_drop
import json

metadata = {'apiLevel': '2.6'}


def run(protocol: protocol_api.ProtocolContext):
    configuration = load_config("basic_transfer_config.json")
    with open('/data/labware/v2/custom_definitions/micronic_96_tuberack_1400ul.json') as labware_file:
        labware_def = json.load(labware_file)
    plate = protocol.load_labware_from_definition(labware_def, 1)
    tiprack_1 = protocol.load_labware(configuration['tiprack'], 5)
    instrument = protocol.load_instrument(configuration['instrument']['model'],
                                          configuration['instrument']['mount'],
                                          tip_racks=[tiprack_1])

    transfers = configuration['transfers']
    for transfer in transfers:
        with pick_up_then_drop(instrument):
            ml = transfer['ml']
            instrument.aspirate(ml, plate[transfer['source_well']])
            instrument.dispense(ml, plate[transfer['target_well']])
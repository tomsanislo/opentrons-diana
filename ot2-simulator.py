from opentrons import simulate
# read the file
protocol_file = open('ot_app.py')
# simulate() the protocol, keeping the runlog
simulate(protocol_file)
# print the runlog
# print(format_runlog(runlog))
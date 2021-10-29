import shelve, os
from ot2_connection_data import OT2ConnectionData

filename = os.path.join(os.getcwd(), "data", "data_connection.out")


d = shelve.open(filename)  # open -- file may get suffix added by low-level
                           # library





# robot = d["2"]        # store data at key (overwrites old data if
                           # using an existing key)
# print(robot.hostname)                           # if no such key)
# del d[key]

connections = d["connections"]

print(connections[0].hostname)

d.close()
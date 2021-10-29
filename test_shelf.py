import shelve, os
from ot2_connection_data import OT2ConnectionData

filename = os.path.join(os.getcwd(), "data", "data_connection.out")


d = shelve.open(filename,"n")  # open -- file may get suffix added by low-level
                           # library

ot2 = OT2ConnectionData()
ot2.hostname = "192.168.10.194"
ot2.username = "root"
ot2.key = "dl_ot2_ssh_key"


robot = OT2ConnectionData()
robot.hostname = "andrey"
robot.username = "ahoj"
robot.key = "dl_ot2_ssh_key"

robot2 = OT2ConnectionData()
robot2.hostname = "andrey2"
robot2.username = "ahoj2"
robot2.key = "dl_ot2_ssh_key2"

connections = [ot2, robot, robot2]

d["len"] = len(connections)

d["connections"] = connections

# d["1"] =  robot  

# d["2"] =  robot2
#         # store data at key (overwrites old data if
                           # using an existing key)
                           # if no such key)
# del d[key]

d.close()
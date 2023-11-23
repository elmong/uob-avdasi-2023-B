#Elmo Cube Heartbeat

import time 
from pymavlink import mavutil

#port = 'tcp:127.0.0.1:5762'
port = 'com5'

connection = mavutil.mavlink_connection(port)

connection.wait_heartbeat()

while True:
    # receive mavlink messages
    msg = connection.recv_match()
    # if no message, continue loop
    if not msg:
        continue
        # get HEARTBEAT message
    if msg.get_type() == 'HEARTBEAT':
        # print message
        print(msg)

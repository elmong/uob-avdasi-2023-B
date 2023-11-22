#Elmo Extracting and filtering data from cube

from pymavlink import mavutil
import numpy as np
import time
import pygame

from global_var import airplane_data
import window_drawing

window_drawing.draw_bad_screen()

port='tcp:127.0.0.1:5762' # simulator 'tcp:127.0.0.1:5762' , cube com#

connection = mavutil.mavlink_connection(port) #connect to local simulator, change to com'number' 

connection.wait_heartbeat() #heartbeat so make sure it's connected to the flight controller

print("Heartbeat from system (system %u component %u)" % (connection.target_system, connection.target_component))

mav_commands = [mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 
                mavutil.mavlink.MAVLINK_MSG_ID_AOA_SSA]

# Refresh rate request
for i in range(len(mav_commands)):
    message = connection.mav.command_long_send(
            connection.target_system,  # Target system ID
            connection.target_component,  # Target component ID
            mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send
            0,  # Confirmation
            mav_commands[i],  # param1: Message ID to be streamed
            0.2*10**6, # param2: Interval in microseconds
            0, 0, 0, 0, 
            0  # target address
            )

while True:

    msg=connection.recv_match()

    if not msg:
        continue
    if msg.get_type() == 'ATTITUDE': #get type of message , check mavlink inspector on missionplanner to get type.
        attitude=msg.to_dict() #extract message to dictionary
        #print(attitude)
        
        yaw=attitude['yaw'] #extract value from dictionary : so 'roll', 'pitch', 'yawspeed'
        airplane_data['yaw'] = yaw
        pitch=attitude['pitch']
        airplane_data['pitch'] = pitch
        roll=attitude['roll']
        airplane_data['roll'] = roll

    if msg.get_type() == 'AOA_SSA': #get type of message , check mavlink inspector on missionplanner to get type.
        aoa_ssa=msg.to_dict()
        airplane_data['aoa'] = aoa_ssa['AOA']

    window_drawing.draw_loop()
    window_drawing.pygame_functions()
    #pygame_functions()
    #pygame_drawing()
    time.sleep(0.001)

#test 
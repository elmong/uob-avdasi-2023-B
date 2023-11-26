#Elmo Extracting and filtering data from cube

from pymavlink import mavutil
from datetime import datetime
import numpy as np
import time
import math
import pygame

from global_var import airplane_data
from global_var import input_commands

import window_drawing

window_drawing.draw_bad_screen()

port='tcp:127.0.0.1:5762' # simulator 'tcp:127.0.0.1:5762' , cube com#

connection = mavutil.mavlink_connection(port) #connect to local simulator, change to com'number' 

connection.wait_heartbeat() #heartbeat so make sure it's connected to the flight controller

print("Heartbeat from system (system %u component %u)" % (connection.target_system, connection.target_component))

mav_commands = [mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 
                mavutil.mavlink.MAVLINK_MSG_ID_AOA_SSA]

refresh_rate_global = 500

# Refresh rate request
for i in range(len(mav_commands)):
    message = connection.mav.command_long_send(
            connection.target_system,  # Target system ID
            connection.target_component,  # Target component ID
            mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send
            0,  # Confirmation
            mav_commands[i],  # param1: Message ID to be streamed
            (1/refresh_rate_global)*10**6, # param2: Interval in microseconds
            0, 0, 0, 0, 
            0  # target address
            )

# def set_servo(enum, pwm_val):
#     message = connection.mav.command_long_send(
#             connection.target_system,  # Target system ID
#             connection.target_component,  # Target component ID
#             mavutil.mavlink.MAV_CMD_DO_SET_SERVO,  # ID of command to send
#             0,  # Confirmation
#             enum,  # param1: Message ID to be streamed
#             pwm_val, # param2: Interval in microseconds
#             0, 0, 0, 0, 
#             0  # target address
#             )

while True:

    msg=connection.recv_match()

    if not msg:
        continue
    if msg.get_type() == 'ATTITUDE': #get type of message , check mavlink inspector on missionplanner to get type.
        attitude=msg.to_dict() #extract message to dictionary
        #print(attitude)
        
        #extract value from dictionary : so 'roll', 'pitch', 'yaw'
        airplane_data['pitch'] = math.degrees(attitude['pitch'])
        airplane_data['pitch_rate'] = math.degrees(attitude['pitchspeed'])
        airplane_data['roll'] = math.degrees(attitude['roll'])
        airplane_data['roll_rate'] = math.degrees(attitude['rollspeed'])
        airplane_data['yaw'] = math.degrees(attitude['yaw'])
        airplane_data['yaw_rate'] = math.degrees(attitude['yawspeed'])

    if msg.get_type() == 'AOA_SSA': #get type of message , check mavlink inspector on missionplanner to get type.
        aoa_ssa=msg.to_dict()
        airplane_data['aoa'] = aoa_ssa['AOA']

    # This is working for sending commands into the sitl
    connection.mav.manual_control_send(connection.target_system,
        int(-input_commands['elevator'] * 1000),
        int(input_commands['aileron'] * 1000),
        1000,
        0,
        0
    )

    # Flight Director Pitch Bar
    input_commands['fd_pitch'] = -airplane_data['pitch']

    #set_servo(3, 1500 + 500*math.sin(time.time()))
    window_drawing.draw_loop()
    window_drawing.pygame_functions()

    time.sleep(0.001)
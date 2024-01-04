#Elmo Extracting and filtering data from cube

from pymavlink import mavutil
from datetime import datetime
import numpy as np
import asyncio
import time
import math

from global_var import airplane_data
from global_var import input_commands

import window_drawing

################################

TESTING_ON_SIM = True
TESTING_GRAPHICS_ONLY = False
port= 'tcp:127.0.0.1:5762' if TESTING_ON_SIM else 'udp:0.0.0.0:14550'
DATA_REFRESH_RATE_GLOBAL = 40

################################

# Refresh rate request
def request_refresh_rate(connection, mav_commands):
    for i in range(len(mav_commands)):
        message = connection.mav.command_long_send(
                connection.target_system,  # Target system ID
                connection.target_component,  # Target component ID
                mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send
                0,  # Confirmation
                mav_commands[i],  # param1: Message ID to be streamed
                (1/DATA_REFRESH_RATE_GLOBAL)*10**6, # param2: Interval in microseconds
                0, 0, 0, 0, 
                0  # target address
                )

def set_servo(connection, enum, pwm_val): ## if you want to use this, remove the manual control command
    message = connection.mav.command_long_send(
            connection.target_system,
            connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 
            0,
            enum,
            pwm_val,
            0, 0, 0, 0, 
            0
            )

################################ THE INITIALISATION STUFF

connection_established = False

################################ LAND OF PREVIOUS VALUES

last_time = time.time()

############################### THE LOOPING STUFF

def update_refresh_rate():
    global last_time
    refresh_rate = 1/(time.time() - last_time)
    airplane_data['refresh_rate'] = refresh_rate
    last_time = time.time()
    # if refresh_rate < 25:
    #     print("WARNING REFRESH RATE TOO LOW: " + str(int(refresh_rate)))

async def mavlink_loop():
    connection = mavutil.mavlink_connection(port) #connect to local simulator, change to com'number' 
    connection.wait_heartbeat() #heartbeat so make sure it's connected to the flight controller
    print("Heartbeat from system (system %u component %u)" % (connection.target_system, connection.target_component))
    mav_commands = [mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 
                    mavutil.mavlink.MAVLINK_MSG_ID_AOA_SSA]
    request_refresh_rate(connection, mav_commands)

    global connection_established
    connection_established = True

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

        # if msg.get_type() == 'SYS_STATUS': #get type of message , check mavlink inspector on missionplanner to get type.
        #     sys_status=msg.to_dict()
        #     print(sys_status['drop_rate_comm'])


        # This is working for sending commands into the sitl
        connection.mav.manual_control_send(connection.target_system,
            int(-input_commands['elevator'] * 1000),
            int(input_commands['aileron'] * 1000),
            1000, # throttle set it at full 1000 for sitl tests
            0,
            0
        )

        # Flight Director Pitch Bar
        input_commands['fd_pitch'] = -airplane_data['pitch']

        update_refresh_rate()

        #set_servo(3, 1500 + 500*math.sin(time.time()))
        await asyncio.sleep(0)

async def pygame_loop():
    while True:
        window_drawing.pygame_draw_loop()
        window_drawing.pygame_update_loop()
        if not connection_established and not TESTING_GRAPHICS_ONLY:
            window_drawing.draw_bad_screen()
        await asyncio.sleep(0)

async def main():
    task1 = asyncio.create_task(pygame_loop())
    if TESTING_GRAPHICS_ONLY:
        await asyncio.gather(task1,)
    else:
        task2 = asyncio.create_task(mavlink_loop())
        await asyncio.gather(task1, task2)

# Run the asyncio event loop
asyncio.run(main())
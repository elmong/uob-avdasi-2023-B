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

TESTING_ON_SIM = False
TESTING_GRAPHICS_ONLY = True
port= 'tcp:127.0.0.1:5762' if TESTING_ON_SIM else 'udp:0.0.0.0:14550'
DATA_REFRESH_RATE_GLOBAL = 30
SUICIDE = False

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

window_drawing.draw_bad_screen()

if not TESTING_GRAPHICS_ONLY:
    connection = mavutil.mavlink_connection(port) #connect to local simulator, change to com'number' 
    connection.wait_heartbeat() #heartbeat so make sure it's connected to the flight controller
    print("Heartbeat from system (system %u component %u)" % (connection.target_system, connection.target_component))
    mav_commands = [mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 
                    mavutil.mavlink.MAVLINK_MSG_ID_VFR_HUD, #vfr hud stands for typical hud data on a fixed wing plane
                    mavutil.mavlink.MAVLINK_MSG_ID_AOA_SSA]
    request_refresh_rate(connection, mav_commands)

################################ LAND OF PREVIOUS VALUES

last_time = time.time()

############################### THE LOOPING STUFF

def update_refresh_rate():
    global last_time
    if (time.time() - last_time) > 0:
        refresh_rate = 1/(time.time() - last_time)
    else:
        refresh_rate = 0
    airplane_data['refresh_rate'] = refresh_rate
    last_time = time.time()
    # if refresh_rate < 25:
    #     print("WARNING REFRESH RATE TOO LOW: " + str(int(refresh_rate)))

def mavlink_loop():

    msg=connection.recv_match()

    if msg:
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

        if msg.get_type() == 'VFR_HUD': #get type of message , check mavlink inspector on missionplanner to get type.
            vfr_hud=msg.to_dict()
            airplane_data['airspeed'] = vfr_hud['airspeed']

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

def pygame_loop():
    window_drawing.pygame_draw_loop()
    window_drawing.pygame_update_loop()

while True:

    if SUICIDE:
        print('\x1b[6;37;41m' + '''
                                                            
                                                            
                NO!                            MNO!         
                MNO!!                         MNNOO!        
               MMNO!                           MNNOO!!      
             MNOONNOO!   MMMMMMMMMMPPPOII!   MNNO!!!!       
             !O! NNO! MMMMMMMMMMMMMPPPOOOII!! NO!           
                   ! MMMMMMMMMMMMMPPPPOOOOIII! !            
                    MMMMMMMMMMMMPPPPPOOOOOOII!!             
                    MMMMMOOOOOOPPPPPPPPOOOOMII!             
                    MMMMM      OPPMMP     ,OMI!             
                    MMMM::   o ,OPMP, o   ::I!!             
                      NNM::: ,,OOPM!P, ::::!!               
                     MMNNNNNOOOOPMO!!IIPPO!!O!              
                     MMMMMNNNNOO:!!:!!IPPPPOO!              
                      MMMMMNNOOMMNNIIIPPPOO!!               
                         MMMONNMMNNNIIIOO!                  
                       MN MOMMMNNNIIIIIO! OO                
                      MNO! IiiiiiiiiiiiI OOOO               
                 NNN MNO!   O!!!!!!!!!O   OONO NO!          
                MNNNNNO!    OOOOOOOOOOO    MMNNON!          
                  MNNNNO!    PPPPPPPPP    MMNON!            
                     OO!                   ON!              
                                                            
                     YOUR SCRIPT IS BROKEN                  
                    CONTACT HENRICK KU GP17                 
                                                            
            ''' + '\x1b[0m')
        quit()

    if TESTING_GRAPHICS_ONLY:
        pygame_loop()
    else:
        mavlink_loop()
        pygame_loop()

        


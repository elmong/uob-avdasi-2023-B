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
DATA_REFRESH_RATE_GLOBAL = 30
SUICIDE = False

################################

CHANNEL_LEFT_AILERON = 1
CHANNEL_LEFT_FLAP = 2
CHANNEL_RIGHT_AILERON = 3
CHANNEL_RIGHT_FLAP = 4
CHANNEL_ELEVATOR = 5
CHANNEL_RUDDER = 6

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
            1500 + pwm_val * 500,
            0, 0, 0, 0, 
            0
            )

def set_param(connection, name, value, type):
    name = name.encode('utf8')
    connection.mav.param_set_send(
        connection.target_system,
        connection.target_component,
        name, value, type
    )
    print(f'set_param({name=}, {value=}, {type=})')
    message = connection.recv_match(type='PARAM_VALUE', blocking=True).to_dict()
    print('name: %s\tvalue: %d' %
          (message['param_id'], message['param_value']))

def init_values():
    set_param(connection, 'STALL_PREVENTION', 0, mavutil.mavlink.MAV_PARAM_TYPE_INT32)
    set_param(connection, 'LIM_PITCH_MAX', 9000, mavutil.mavlink.MAV_PARAM_TYPE_INT32)
    set_param(connection, 'LIM_PITCH_MIN', -9000, mavutil.mavlink.MAV_PARAM_TYPE_INT32)
    set_param(connection, 'LIM_ROLL_CD', 9000, mavutil.mavlink.MAV_PARAM_TYPE_INT32)
    
    for i in range(1, 17):  # 16 Chanels
        param_name = f'SERVO{i}_FUNCTION'
        set_param(connection, param_name, 0, mavutil.mavlink.MAV_PARAM_TYPE_INT32)
        param_name = f'SERVO{i}_MIN'
        set_param(connection, param_name, 1000, mavutil.mavlink.MAV_PARAM_TYPE_INT32)
        param_name = f'SERVO{i}_MAX'
        set_param(connection, param_name, 2000, mavutil.mavlink.MAV_PARAM_TYPE_INT32)

################################ THE INITIALISATION STUFF

if not TESTING_GRAPHICS_ONLY:
    window_drawing.draw_bad_screen()
    connection = mavutil.mavlink_connection(port) #connect to local simulator, change to com'number' 
    connection.wait_heartbeat() #heartbeat so make sure it's connected to the flight controller
    print("Heartbeat from system (system %u component %u)" % (connection.target_system, connection.target_component))
    mav_commands = [mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 
                    mavutil.mavlink.MAVLINK_MSG_ID_VFR_HUD, #vfr hud stands for typical hud data on a fixed wing plane
                    mavutil.mavlink.MAVLINK_MSG_ID_AOA_SSA]
    request_refresh_rate(connection, mav_commands)

window_drawing.draw_init_screen()
init_values()

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

def fetch_messages_and_update():
    try:
        msg=connection.recv_match(blocking=True) ## THE BIG BLOCK BELOW IS USED TO EXTRACT DATA FROM MSG AND FEED INTO COMMON TABLE

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

            input_commands['fd_pitch'] = -airplane_data['pitch']

    except Exception as e:
        # print("Error : {e}")
        print("CONNECTION LOST!")

def flight_controller():
    flap_angle = (input_commands['flap_setting']-1)

    set_servo(connection, CHANNEL_LEFT_AILERON, input_commands['aileron'])
    set_servo(connection, CHANNEL_RIGHT_AILERON, -input_commands['aileron'])
    set_servo(connection, CHANNEL_ELEVATOR, input_commands['elevator'])
    set_servo(connection, CHANNEL_RUDDER, 0)
    set_servo(connection, CHANNEL_LEFT_FLAP, flap_angle)
    set_servo(connection, CHANNEL_RIGHT_FLAP, flap_angle)

def mavlink_loop():
    # Flight Director Pitch Bar
    fetch_messages_and_update()
    update_refresh_rate()
    flight_controller()

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

        


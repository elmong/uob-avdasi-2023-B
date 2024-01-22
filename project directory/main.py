#Elmo Extracting and filtering data from cube

from pymavlink import mavutil
from datetime import datetime
import time
import math
import csv
import os

from global_var import *

import window_drawing

root_path = os.path.abspath(os.path.dirname(__file__))

################################

TESTING_ON_SIM = True
TESTING_GRAPHICS_ONLY = True
TESTING_REAL_PLANE_CHANNELS = False # Testing channels on sim? Or testing servos on real plane? 
port= 'tcp:127.0.0.1:5762' if TESTING_ON_SIM else 'udp:0.0.0.0:14550'
DATA_REFRESH_RATE_GLOBAL = 30 # Hz
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
    set_param(connection, 'ACRO_LOCKING', 0, mavutil.mavlink.MAV_PARAM_TYPE_INT32)
    
    if TESTING_REAL_PLANE_CHANNELS:
        for i in range(1, 17):  # 16 Chanels
            param_name = f'SERVO{i}_FUNCTION'
            set_param(connection, param_name, 0, mavutil.mavlink.MAV_PARAM_TYPE_INT32)
            param_name = f'SERVO{i}_MIN'
            set_param(connection, param_name, 1000, mavutil.mavlink.MAV_PARAM_TYPE_INT32)
            param_name = f'SERVO{i}_MAX'
            set_param(connection, param_name, 2000, mavutil.mavlink.MAV_PARAM_TYPE_INT32)
    else:
        param_name = 'SERVO1_FUNCTION'
        set_param(connection, param_name, 4, mavutil.mavlink.MAV_PARAM_TYPE_INT32)
        param_name = 'SERVO2_FUNCTION'
        set_param(connection, param_name, 19, mavutil.mavlink.MAV_PARAM_TYPE_INT32)
        param_name = 'SERVO3_FUNCTION'
        set_param(connection, param_name, 70, mavutil.mavlink.MAV_PARAM_TYPE_INT32)
        param_name = 'SERVO4_FUNCTION'
        set_param(connection, param_name, 21, mavutil.mavlink.MAV_PARAM_TYPE_INT32)

def logging_to_csv(filename, *args):
    with open(os.path.join(root_path, 'logdata', filename), 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(args)

saved_starttime_flag = False
logging_start_time = 0
filename = ''
def mavlink_logging():
    global saved_starttime_flag
    global logging_start_time
    global filename
    if ui_commands['logging'] and not saved_starttime_flag:
        logging_start_time = time.time()
        saved_starttime_flag = True
        print('Start Logging')
        filename = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime(logging_start_time)) + '.csv'
        print(filename)
    elif ui_commands['logging']:
        logging_elapsed_time = time.time() - logging_start_time
        logging_to_csv( filename,
                        logging_elapsed_time,
                        airplane_data['pitch'],
                        airplane_data['roll'],
                        airplane_data['yaw']
                        )
    else:
        logging_start_time = 0
        saved_starttime_flag = False
        filename = ''

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
if not TESTING_GRAPHICS_ONLY:
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

    ################## WARNING ##################
    # Do NOT do: 
    #
    #   msg=connection.recv_match() 
    #   if msg:
    #       if msg.get_type() == 'ATTITUDE': 
    #           attitude=msg.to_dict() 
    #
    # That way you are fetching the entire message then filtering. The message is massive
    # and will NOT run at 30Hz. 
    # For 30Hz or even 60Hz, EXTRACT NEEDED DATA ONLY!
    #
    # attitude = connection.recv_match(type = 'ATTITUDE')
    # if attitude is not None:
    #   attitude = attitude.to_dict()
    #
    # This will guarantee 1. Only needed stuff is requested, and 2. If messgae not received
    # just move on to the pygame loop to keep the fps.

    attitude = connection.recv_match(type = 'ATTITUDE') #extract message to dictionary
    #print(attitude)
    if attitude is not None:
        attitude = attitude.to_dict()
    #extract value from dictionary : so 'roll', 'pitch', 'yaw'
        airplane_data['pitch'] = math.degrees(attitude['pitch'])
        airplane_data['pitch_rate'] = math.degrees(attitude['pitchspeed'])
        airplane_data['roll'] = math.degrees(attitude['roll'])
        airplane_data['roll_rate'] = math.degrees(attitude['rollspeed'])
        airplane_data['yaw'] = math.degrees(attitude['yaw'])
        airplane_data['yaw_rate'] = math.degrees(attitude['yawspeed'])

    aoa_ssa = connection.recv_match(type = 'AOA_SSA')
    if aoa_ssa is not None:
        aoa_ssa = aoa_ssa.to_dict()
        airplane_data['aoa'] = aoa_ssa['AOA']

    vfr_hud = connection.recv_match(type = 'VFR_HUD')
    if vfr_hud is not None:
        vfr_hud = vfr_hud.to_dict()
        airplane_data['airspeed'] = vfr_hud['airspeed']

    # if msg.get_type() == 'SYS_STATUS': #get type of message , check mavlink inspector on missionplanner to get type.
    #     sys_status=msg.to_dict()
    #     print(sys_status['drop_rate_comm'])

    input_commands['fd_pitch'] = -airplane_data['pitch']

def flight_controller():
    flap_angle = (input_commands['flap_setting']-1)

    if TESTING_REAL_PLANE_CHANNELS:
        set_servo(connection, CHANNEL_LEFT_AILERON, input_commands['aileron'])
        set_servo(connection, CHANNEL_RIGHT_AILERON, -input_commands['aileron'])
        set_servo(connection, CHANNEL_ELEVATOR, input_commands['elevator'])
        set_servo(connection, CHANNEL_RUDDER, 0)
        set_servo(connection, CHANNEL_LEFT_FLAP, flap_angle)
        set_servo(connection, CHANNEL_RIGHT_FLAP, flap_angle)

msg_or_ctrl_flag = False
def mavlink_loop():
    # Flight Director Pitch Bar
    global msg_or_ctrl_flag

    fetch_messages_and_update()
    flight_controller()
    update_refresh_rate()

def pygame_loop():
    window_drawing.pygame_draw_loop()
    window_drawing.pygame_update_loop()

while True:

    if TESTING_GRAPHICS_ONLY:
        pygame_loop()
    else:
        mavlink_loop()
        pygame_loop()
    mavlink_logging()


#Elmo Extracting and filtering data from cube

from pymavlink import mavutil
from datetime import datetime
import asyncio
import time
import time
import math
import csv
import os
import serial

from math_helpers import *
from global_var import *
import GCS_serial_reader
import pico_class
from PID import *

import window_drawing

root_path = os.path.abspath(os.path.dirname(__file__))

################################

TESTING_ON_SIM = False
TESTING_GRAPHICS_ONLY = False
TESTING_REAL_PLANE_CHANNELS = True # Testing channels on sim? Or testing servos on real plane? 
port= 'tcp:127.0.0.1:5762' if TESTING_ON_SIM else 'udp:0.0.0.0:14550'
DATA_REFRESH_RATE_GLOBAL = 30 # Hz
DELTA_TIME = 0.01
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
            
class Servo:
    def __init__(self, channel_num):
        self.val = 0
        self.prev_val = 0
        self.channel_num = channel_num
        self.prev_set_time = time.time()
    def set_val(self, val):
        rate_limit = 0.1
        if (time.time() - self.prev_set_time) > 0:
            self.val = val
            #print((self.val, self.prev_val))
            if (self.val - self.prev_val) > 0:
                self.val = min(self.prev_val + rate_limit, self.val)
            else:
                self.val = max(self.prev_val-rate_limit, self.val)
            set_servo(connection, self.channel_num, self.val)
            self.prev_val = self.val
    def get_val(self):
        return self.val

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


#declare pico objects
pico0 = pico_class.Pico(0, None , False, coms_ports['pico0'], -1)
pico1 = pico_class.Pico(1, None , False, coms_ports['pico1'], None)
pico2 = pico_class.Pico(2, None , False, coms_ports['pico2'], None)
pico3 = pico_class.Pico(3, None , False, coms_ports['pico3'], None)
pico4 = pico_class.Pico(4, None , False, coms_ports['pico4'], None)
pico5 = pico_class.Pico(5, None , False, coms_ports['pico5'], None)

pico_array = [pico0,pico1,pico2,pico3,pico4,pico5]
#pico_array = [pico0]

def connect_picos():
    #if pico connections are closed, attempt connection
    for item in pico_array:
        item.close_connection()
        item.initialize_connection()


def collect_pico_msgs(): #collects all of the picos' messages
    for item in pico_array:
        item.read_message()
        # print(angle_sensor_data_live['sensor2'])


################################ LAND OF PREVIOUS VALUES

last_time = time.time()

############################### THE LOOPING STUFF

import time

mavlink_loop_timer = Timer()
pico_loop_timer = Timer()
mavlink_loop_rate_filter = MovingAverage(20)
pico_loop_rate_filter = MovingAverage(5)

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

        mavlink_loop_timer.update() # Move the counter to the not none loop
        mavlink_loop_rate_filter.update(mavlink_loop_timer.get_refresh_rate())
        airplane_data['mavlink_refresh_rate'] = mavlink_loop_rate_filter.get_value()

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

LEFT_AILERON = Servo(CHANNEL_LEFT_AILERON)
RIGHT_AILERON = Servo(CHANNEL_RIGHT_AILERON)
ELEVATOR = Servo(CHANNEL_ELEVATOR)
RUDDER = Servo(CHANNEL_RUDDER)
LEFT_FLAP = Servo(CHANNEL_LEFT_FLAP)
RIGHT_FLAP = Servo(CHANNEL_RIGHT_FLAP)

pitch_pid = Pid_controller(0.1, 0.000, 0.06, (-1,1), 10)
flap_damper = SmoothDamp()
aileron_damper = SmoothDamp()
prev_flap_angle = 0
prev_aileron_angle = 0

def flight_controller():
    if TESTING_REAL_PLANE_CHANNELS:
        global prev_flap_angle
        flap_angle = flap_damper.smooth_damp( (input_commands['flap_setting']-1), 1.2, 1.5, mavlink_loop_timer.DELTA_TIME)
        prev_flap_angle = flap_angle

        global prev_aileron_angle
        aileron_angle = aileron_damper.smooth_damp( input_commands['aileron'], 0.5, 1.5, mavlink_loop_timer.DELTA_TIME)
        prev_aileron_angle = aileron_angle

        l_ail_demand_ang = 0
        if aileron_angle >= 0:
            l_ail_demand_ang = aileron_angle * 0.85
        else:
            l_ail_demand_ang = aileron_angle
        l_ail_demand_ang -= 0.1
        
        LEFT_AILERON.set_val(l_ail_demand_ang)
        RIGHT_AILERON.set_val(-aileron_angle)

        cmd = pitch_pid.update(input_commands['fd_pitch'], airplane_data['pitch'], mavlink_loop_timer.DELTA_TIME)
        input_commands['pitch_pid'] = pitch_pid.output_unclamped
        if not input_commands['ap_on']:
            ELEVATOR.set_val(-input_commands['elevator'])
            input_commands['pitch_pid'] = 0
            pitch_pid.integrator = 0
        else:
            ELEVATOR.set_val(-cmd)
        RUDDER.set_val(0)
        LEFT_FLAP.set_val(-flap_angle * 0.4)
        RIGHT_FLAP.set_val(flap_angle)

def update_servo_commands():
    control_surfaces['left_aileron']['servo_demand'] = LEFT_AILERON.get_val()
    control_surfaces['left_flap']['servo_demand'] = LEFT_FLAP.get_val()
    control_surfaces['right_aileron']['servo_demand'] = RIGHT_AILERON.get_val()
    control_surfaces['right_flap']['servo_demand'] = RIGHT_FLAP.get_val()
    control_surfaces['elevator']['servo_demand'] = ELEVATOR.get_val()
    control_surfaces['rudder']['servo_demand'] = RUDDER.get_val()

def not_async_pygame_loop(): ## For the sake of debugging with graphics only.
    while True:
        window_drawing.pygame_draw_loop()
        window_drawing.pygame_update_loop()

async def pygame_loop():
    while True:
        window_drawing.pygame_draw_loop()
        window_drawing.pygame_update_loop()
        await asyncio.sleep(0)

async def mavlink_loop():
    while True:
        if ui_commands['force_refresh'] == 1:
            print('Force Refresh')
            request_refresh_rate(connection, mav_commands)
            ui_commands['force_refresh'] = 0
        fetch_messages_and_update()
        flight_controller()
        update_servo_commands()
        
        mavlink_logging()
        await asyncio.sleep(0)

connect_picos()
async def pico_loop(): #where all of the pico's events are handled
    while True:
        collect_pico_msgs()

        if ui_commands['pico_refresh_com'] == 1:
            connect_picos()
            ui_commands['pico_refresh_com'] = 0

        pico_loop_timer.update()
        pico_loop_rate_filter.update(pico_loop_timer.get_refresh_rate())
        airplane_data['pico_refresh_rate'] = pico_loop_rate_filter.get_value()
        await asyncio.sleep(0)

async def async_loop():
    task1 = asyncio.create_task(mavlink_loop())
    task2 = asyncio.create_task(pygame_loop())
    task3 = asyncio.create_task(pico_loop())
    await asyncio.gather(task1, task2, task3)

if TESTING_GRAPHICS_ONLY:
    while True:
        not_async_pygame_loop()
else:
    asyncio.run(async_loop())




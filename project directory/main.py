#Elmo Extracting and filtering data from cube

from pymavlink import mavutil
from datetime import datetime
import asyncio
import time
import time
import math
import csv
import os
import sys
import serial
import threading

from math_helpers import *
from global_var import *
from global_func import *
import GCS_serial_reader
import pico_class
from PID import *

GCS_BEGIN_PROGRAM() ## DO NOT MOVE THIS ELSEWHERE!
# Once global var is loaded, directly inject the saved json. Otherwise objects created in window drawing will have wrong initial values

import window_drawing
import live_plotter_class

root_path = os.path.abspath(os.path.dirname(__file__))

import csv_plotflightdata

################################

TESTING_ON_SIM = True
TESTING_GRAPHICS_ONLY = False
TESTING_REAL_PLANE_CHANNELS = False # Testing channels on sim? Or testing servos on real plane? 
TESTING_DO_BOKEH = False
port= 'tcp:127.0.0.1:5762' if TESTING_ON_SIM else 'udp:0.0.0.0:14550'
DATA_REFRESH_RATE_GLOBAL = 30 # Hz
DELTA_TIME = 0.01
SERVO_RATE_LIMIT = 5

SUICIDE = False

################################

CHANNEL_LEFT_AILERON = 1
CHANNEL_LEFT_FLAP = 2
CHANNEL_RIGHT_AILERON = 3
CHANNEL_RIGHT_FLAP = 4
CHANNEL_ELEVATOR = 5
CHANNEL_RUDDER = 6

SERVO_BOOTUP_INTEVRAL = 0.5
SERVO_BOOTUP_TIME_TOTAL = 4

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

def set_servo(connection, enum, ratio): ## if you want to use this, remove the manual control command
    pwm_val = ratio_to_pwm(ratio)
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
            
class Servo:
    def __init__(self, channel_num, start_pos): # start_pos is -1 to 1, to prevent jerk
        self.val = start_pos
        self.prev_val = start_pos
        self.channel_num = channel_num
        self.prev_set_time = time.time()
    def set_val(self, val):
        bootup_timer = flight_elapsed_time.get_time()
        rate_limit = SERVO_RATE_LIMIT
        if bootup_timer < SERVO_BOOTUP_TIME_TOTAL:
            rate_limit = SERVO_RATE_LIMIT/3
        rate_limit = rate_limit * flight_controller_timer.DELTA_TIME_SMOOTH
        if (time.time() - self.prev_set_time) > 0 and (bootup_timer > self.channel_num*SERVO_BOOTUP_INTEVRAL):
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
            set_param(connection, param_name, 1, mavutil.mavlink.MAV_PARAM_TYPE_INT32)
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
                        airplane_data['yaw'],
                        airplane_data["airspeed"],
                        airplane_data["aoa"],
                        control_surfaces["port_aileron"]["servo_demand"],
                        control_surfaces["port_aileron"]["angle"],
                        control_surfaces["port_flap"]["servo_demand"],
                        control_surfaces["port_flap"]["angle"],
                        control_surfaces["starboard_aileron"]["servo_demand"],
                        control_surfaces["starboard_aileron"]["angle"],
                        control_surfaces["starboard_flap"]["servo_demand"],
                        control_surfaces["starboard_flap"]["angle"],
                        control_surfaces["elevator"]["servo_demand"],
                        control_surfaces["elevator"]["angle"],
                        control_surfaces["rudder"]["servo_demand"],
                        control_surfaces["rudder"]["angle"]
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
                    mavutil.mavlink.MAVLINK_MSG_ID_AOA_SSA,
                    mavutil.mavlink.MAVLINK_MSG_ID_SERVO_OUTPUT_RAW]
    request_refresh_rate(connection, mav_commands)

window_drawing.draw_init_screen()
if not TESTING_GRAPHICS_ONLY:
    init_values()


#declare pico objects
pico0 = pico_class.Pico(0, None , False, coms_ports['pico0'], None)
pico1 = pico_class.Pico(1, None , False, coms_ports['pico1'], None)
pico2 = pico_class.Pico(2, None , False, coms_ports['pico2'], None)
pico3 = pico_class.Pico(3, None , False, coms_ports['pico3'], None)
pico4 = pico_class.Pico(4, None , False, coms_ports['pico4'], None)
pico5 = pico_class.Pico(5, None , False, coms_ports['pico5'], None)

pico_array = [pico0,pico1,pico2,pico3,pico4,pico5]

def connect_picos():
    #if pico connections are closed, attempt connection
    for item in pico_array:
        item.close_connection()
        item.initialize_connection()


def collect_pico_msgs(): #collects all of the picos' messages
    for item in pico_array:
        item.read_message()

#declare live data visualisation servers
control_surface_plot = live_plotter_class.Live_plotter(80)
control_surface_plot.create_datasets("elevator", "rudder", "port_aileron", "port_flap","starboard_aileron","starboard_flap","elevator", "rudder", "port_aileron", "port_flap","starboard_aileron","starboard_flap","actual_pitch","demanded_pitch")

################################ LAND OF PREVIOUS VALUES

last_time = time.time()

############################### THE LOOPING STUFF

import time

mavlink_loop_timer = Timer() # This is purely for display purposes of the messages recv rate
flight_controller_timer = Timer() # This is for timing the servo rate limiters
pico_loop_timer = Timer()
mavlink_loop_rate_filter = MovingAverage(20) # Filters stuff out for display
pico_loop_rate_filter = MovingAverage(5)

flight_elapsed_time = Stopwatch()
flight_elapsed_time.start()

prev_gcs_in_control = True

def flip_servo_modes_tmx_gcs():
    global prev_gcs_in_control
    if TESTING_REAL_PLANE_CHANNELS:
        if prev_gcs_in_control != input_commands['gcs_in_control']:
            if input_commands['gcs_in_control']:
                for i in range(1, 7):  # only 6 channels modified
                    param_name = f'SERVO{i}_FUNCTION'
                    set_param(connection, param_name, 0, mavutil.mavlink.MAV_PARAM_TYPE_INT32)
                prev_gcs_in_control = input_commands['gcs_in_control']
                print('***********GCS TAKEOVER***********')
            else:
                for i in range(1, 7):  # 6 Chanels
                    param_name = f'SERVO{i}_FUNCTION'
                    set_param(connection, param_name, 1, mavutil.mavlink.MAV_PARAM_TYPE_INT32)
                prev_gcs_in_control = input_commands['gcs_in_control']
                print('***********TMX TAKEOVER***********')

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

    servo_pos_msg = connection.recv_match(type = 'SERVO_OUTPUT_RAW')
    if servo_pos_msg is not None:
        servo_pos_msg = servo_pos_msg.to_dict()
        control_surfaces['elevator']['servo_actual_pwm'] = servo_pos_msg['servo5_raw']
        control_surfaces['rudder']['servo_actual_pwm'] = servo_pos_msg['servo6_raw']
        control_surfaces['port_aileron']['servo_actual_pwm'] = servo_pos_msg['servo1_raw']
        control_surfaces['port_flap']['servo_actual_pwm'] = servo_pos_msg['servo2_raw']
        control_surfaces['starboard_aileron']['servo_actual_pwm'] = servo_pos_msg['servo3_raw']
        control_surfaces['starboard_flap']['servo_actual_pwm'] = servo_pos_msg['servo4_raw']


    # if msg.get_type() == 'SYS_STATUS': #get type of message , check mavlink inspector on missionplanner to get type.
    #     sys_status=msg.to_dict()
    #     print(sys_status['drop_rate_comm'])

LEFT_AILERON = Servo(CHANNEL_LEFT_AILERON, start_pos = control_surfaces['port_aileron']['servo_actual'])
LEFT_FLAP = Servo(CHANNEL_LEFT_FLAP, start_pos = control_surfaces['port_flap']['servo_actual'])
RIGHT_AILERON = Servo(CHANNEL_RIGHT_AILERON, start_pos = control_surfaces['starboard_aileron']['servo_actual'])
RIGHT_FLAP = Servo(CHANNEL_RIGHT_FLAP, start_pos = control_surfaces['starboard_flap']['servo_actual'])
ELEVATOR = Servo(CHANNEL_ELEVATOR, start_pos = control_surfaces['elevator']['servo_actual'])
RUDDER = Servo(CHANNEL_RUDDER, start_pos = control_surfaces['rudder']['servo_actual'])

pitch_pid = Pid_controller(PID_values['output_limits'], 1)
flap_damper = SmoothDamp()
aileron_damper = SmoothDamp()
prev_flap_angle = 0
prev_aileron_angle = 0

def elevator_feedback():
    error = 0
    gain = 0.05
    if control_surfaces['elevator']['feedback_mode']:
        ideal_deflection = input_commands['elevator']  * 45
        actual_deflection = control_surfaces['elevator']['angle']
        error = (ideal_deflection - actual_deflection) * gain
    return error

def flight_controller():
    cmd, cmd_unclamped = pitch_pid.update(input_commands['fd_pitch'], airplane_data['pitch'], flight_controller_timer.DELTA_TIME_SMOOTH, PID_values['Kp'], PID_values['Ki'], PID_values['Kd'], feed_in_rate = airplane_data['pitch_rate'])
    # Now, the kp of the pid is in units: (Degree of elevator deflection per degree of pitch error)
    input_commands['pitch_pid'] = cmd / 45 # divide by 45 deg to get true elevator deflection
    input_commands['pitch_pid_unclamped'] = cmd_unclamped / 45
    if not input_commands['ap_on']:
        input_commands['pitch_pid'] = 0
        input_commands['pitch_pid_unclamped'] = 0
        pitch_pid.reset_integrator()

    if TESTING_REAL_PLANE_CHANNELS:
        global prev_flap_angle
        flap_angle = flap_damper.smooth_damp( (input_commands['flap_setting']-1), 0.1, 5, flight_controller_timer.DELTA_TIME)
        prev_flap_angle = flap_angle

        if not control_surfaces['port_aileron']['manual_control']:
            control_surfaces['port_aileron']['servo_demand'] = interpolator_port_aileron.value(input_commands['aileron'])
        if not control_surfaces['starboard_aileron']['manual_control']:
            control_surfaces['starboard_aileron']['servo_demand'] = interpolator_starboard_aileron.value(input_commands['aileron'])
        if not control_surfaces['port_flap']['manual_control']:
            control_surfaces['port_flap']['servo_demand'] = interpolator_port_flap.value(flap_angle)
        if not control_surfaces['starboard_flap']['manual_control']:
            control_surfaces['starboard_flap']['servo_demand'] = interpolator_starboard_flap.value(flap_angle)
        if not control_surfaces['elevator']['manual_control']:
            foo = 0
            if not input_commands['ap_on']:
                foo = clamper(input_commands['elevator'], -1, 1)
            else:
                input_commands['elevator'] = input_commands['pitch_pid']
                foo = clamper(input_commands['pitch_pid'], -1, 1) # Has to be -1 to 1 because this is setting 

            foo = clamper(foo  + elevator_feedback(), -1, 1)
            control_surfaces['elevator']['servo_demand'] = interpolator_elevator.value(foo)

        if not control_surfaces['rudder']['manual_control']:
            control_surfaces['rudder']['servo_demand'] = interpolator_rudder.value(input_commands['aileron'])

        ################################################## Boilerplate

        if input_commands['gcs_in_control']:
            LEFT_AILERON.set_val(control_surfaces['port_aileron']['servo_demand'])
            RIGHT_AILERON.set_val(control_surfaces['starboard_aileron']['servo_demand'])
            ELEVATOR.set_val(control_surfaces['elevator']['servo_demand'])
            RUDDER.set_val(control_surfaces['rudder']['servo_demand'])
            LEFT_FLAP.set_val(control_surfaces['port_flap']['servo_demand'])
            RIGHT_FLAP.set_val(control_surfaces['starboard_flap']['servo_demand'])

        control_surfaces['port_aileron']['servo_actual'] = LEFT_AILERON.get_val()
        control_surfaces['starboard_aileron']['servo_actual'] = RIGHT_AILERON.get_val()
        control_surfaces['elevator']['servo_actual'] = ELEVATOR.get_val()
        control_surfaces['rudder']['servo_actual'] = RUDDER.get_val()
        control_surfaces['port_flap']['servo_actual'] = LEFT_FLAP.get_val()
        control_surfaces['starboard_flap']['servo_actual'] = RIGHT_FLAP.get_val()
    
    flight_controller_timer.update()

async def mavlink_loop():
    while True:
        if ui_commands['force_refresh'] == 1:
            print('Force Refresh')
            request_refresh_rate(connection, mav_commands)
            ui_commands['force_refresh'] = 0
        flip_servo_modes_tmx_gcs()
        fetch_messages_and_update()
        flight_controller()
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

async def instant_plot_loop():
    while True:
        if ui_commands['csv_plot'] == 1:
            csv_plotflightdata.plot_the_csv_output()
            ui_commands['csv_plot'] = 0
        await asyncio.sleep(0)

def live_data_plot_ini():
    control_surface_plot.ini()
    
async def pygame_loop():
    while True:
        window_drawing.pygame_draw_loop()
        window_drawing.pygame_update_loop()
        await asyncio.sleep(0)

async def async_loop():
    task1 = asyncio.create_task(mavlink_loop())
    task2 = asyncio.create_task(pygame_loop())
    task3 = asyncio.create_task(pico_loop())
    task4 = asyncio.create_task(instant_plot_loop())
    await asyncio.gather(task1, task2, task3, task4)

#tasks set to run only when graphics only is true
async def graphics_only_async_loop():
    task3 = asyncio.create_task(pygame_loop())
    task4 = asyncio.create_task(instant_plot_loop())
    await asyncio.gather(task3, task4)

def worker():
    #creating a thread for live data plotter server (because it's a blocking function that is already running an asyncio loop)
    #control_surface_plot.server.io_loop.add_callback(control_surface_plot.server.show, "/")
    #control_surface_plot.server.io_loop.add_callback(control_surface_plot.update_data_dictionaries_control_surfaces)
    sl = control_surface_plot.server.io_loop.start()
    execute_polling_coroutines_forever(sl)
    return

def quit_func():
    #needed to stop live data plotting server
    #doesnt do anything as it is never called
    control_surface_plot.shutdown()
    quit()

if TESTING_DO_BOKEH:
    live_data_plot_ini()
    t = threading.Thread(target=worker)
    t.start()

if TESTING_GRAPHICS_ONLY:
    ml = asyncio.run(graphics_only_async_loop())  
else:
    ml = asyncio.run(async_loop())
    




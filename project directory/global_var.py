# GLOBAL VARIABLES OPEN TO ACCESS
from math_helpers import Interpolator

airplane_data = {
    'pitch': 0,
    'pitch_rate': 0,
    'roll': 0,
    'roll_rate': 0,
    'yaw': 0,
    'yaw_rate': 0,
    'aoa': 0,
    'airspeed': 0,
    'mavlink_refresh_rate': 0,
    'pico_refresh_rate': 0,
}
    
input_commands = {
    'elevator': 0,
    'aileron': 0,
    'rudder': 0,
    'throttle': 0,
    'gcs_in_control' : True,
    'ap_on' : False,
    'fd_pitch': 0,
    'pitch_pid': 0,
    'pitch_pid_unclamped': 0,
    'flap_setting': 0, # this is the position, 0:UP 1:TO 2:LDG
}

control_surfaces = {
    "port_aileron": {
        "servo_demand": 0,
        "servo_actual": 0, # rate limited
        "servo_actual_pwm":0, # stores pwm given by cube
        "angle": 0,
        "manual_control": False,
        "feedback_mode": False,
    },
    "port_flap": {
        "servo_demand": 0,
        "servo_actual": 0,
        "servo_actual_pwm":0,
        "angle": 0,
        "manual_control": False,
        "feedback_mode": False,
    },
    "starboard_aileron": {
        "servo_demand": 0,
        "servo_actual": 0,
        "servo_actual_pwm":0,
        "angle": 0,
        "manual_control": False,
        "feedback_mode": False,
    },
    "starboard_flap": {
        "servo_demand": 0,
        "servo_actual": 0,
        "servo_actual_pwm":0,
        "angle": 0,
        "manual_control": False,
        "feedback_mode": False,
    },
    "elevator": {
        "servo_demand": 0,
        "servo_actual": 0,
        "servo_actual_pwm":0,
        "angle": 0,
        "manual_control": False,
        "feedback_mode": False,
    },
    "rudder": {
        "servo_demand": 0,
        "servo_actual": 0,
        "servo_actual_pwm":0,
        "angle": 0,
        "manual_control": False,
        "feedback_mode": False,
    }
}

ui_commands = {
    'logging' : False,
    'force_refresh': 0, # This is to force the refresh rate back to speed after a current kill
    'pico_refresh_com' : 0,
    'csv_plot': 0,
}

#Ports/connection addresses used
coms_ports = {
    #pico# does not have to match pico ID, just generic assignment of ports to picos
    'pico0' : 'COM6',
    'pico1' : 'COM8',
    'pico2' : 'COM13',
    'pico3' : 'COM13',
    'pico4' : 'COM13',
    'pico5' : 'COM13'
}

#pico connection status
pico_status = {
    'pico0' : False,
    'pico1' : False,
    'pico2' : False,
    'pico3' : False,
    'pico4' : False,
    'pico5' : False
}

#GCS Serial Reader Message Size in Bytes
serial_reader_msg_size = 50

#file path to store data to
file_path = 'Results.csv'

PID_values = {
    'Kp' : 4, # how many degrees of elevator (del e) per degree of pitch error?
    'Ki' : 0,
    'Kd' : 1,
    'setpoint' : 0,
    'output_limits' : [-45,45]
}


interpolator_port_aileron = Interpolator([
    (-1, -0.3), 
    (0, 0.05), 
    (1, 0.3)])
interpolator_port_flap = Interpolator(
    [(-1, -0.23), 
     (0, -0.15), 
     (1, 0)])
interpolator_starboard_aileron = Interpolator(
    [(-1, -1), 
     (0, -0.73), 
     (1, 0)])
interpolator_starboard_flap = Interpolator(
    [(-1, -1), 
     (0, -0.74), 
     (1, -0.24)])
interpolator_elevator = Interpolator(
    [(-1, 0.36), 
     (0, -0.12),  
     (1, -0.69)])
interpolator_rudder = Interpolator(
    [(-1, -0.7), 
     (0, 0), 
     (1, 0.63)])
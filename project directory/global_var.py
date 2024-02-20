# GLOBAL VARIABLES OPEN TO ACCESS

airplane_data = {
    'pitch': 0,
    'pitch_rate': 0,
    'pitch_rate_earth': 0,
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
        "angle": 0,
        "manual_control": False,
    },
    "port_flap": {
        "servo_demand": 0,
        "servo_actual": 0,
        "angle": 0,
        "manual_control": False,
    },
    "starboard_aileron": {
        "servo_demand": 0,
        "servo_actual": 0,
        "angle": 0,
        "manual_control": False,
    },
    "starboard_flap": {
        "servo_demand": 0,
        "servo_actual": 0,
        "angle": 0,
        "manual_control": False,
    },
    "elevator": {
        "servo_demand": 0,
        "servo_actual": 0,
        "angle": 0,
        "manual_control": False,
    },
    "rudder": {
        "servo_demand": 0,
        "servo_actual": 0,
        "angle": 0,
        "manual_control": False,
    }
}

ui_commands = {
    'logging' : False,
    'force_refresh': 0, # This is to force the refresh rate back to speed after a current kill
    'pico_refresh_com' : 0,
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
serial_reader_msg_size = 32

#file path to store data to
file_path = 'Results.csv'

PID_values = {
    'Kp' : 4, # how many degrees of elevator (del e) per degree of pitch error?
    'Ki' : 0,
    'Kd' : 1,
    'setpoint' : 0,
    'output_limits' : [-45,45]
}

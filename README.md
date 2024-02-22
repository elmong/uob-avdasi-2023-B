#I TOLD YOU NOT TO LOOK!

project directory/ is where most of the thing happens

Control surfaces system:
TP:
  Elevator TMS/RCS
  Rudder RCS
  
Wing
  Flaps TMS, RCS failsafe
  Aileron RCS

# _DOCUMENDATION:
There are a few important files in this main ground control repository.
\project directory contains the main project, with the master script being main.py.
window_drawing.py is imported with functions for draw loops.
global_var.py is a master script to bridge across Group 17 and 18's work. That is where Group 18 should feed in their data.

In the future, PID should feed in their controller outputs at main.py for cleanness sake.

## Code Explanation

First of all, we need to set up the port in main.py.
Below is the port for SITL:
```python
port='tcp:127.0.0.1:5762'
```
And this is the port for cubeorange via wifi:
```python
0.0.0.0.14550
```

Then, we request establishment of a datastream via the following functions:
```python
connection = mavutil.mavlink_connection(port) #connect to local simulator, change to com'number' 
connection.wait_heartbeat() #heartbeat so make sure it's connected to the flight controller
print("Heartbeat from system (system %u component %u)" % (connection.target_system, connection.target_component))
```

The below code snippet sets the refresh rate of the system. Request the rate ONCE during initialisation, do not have to send multiple request for the same frequency or it is just using up bandwidth on the wifi.
```python
for i in range(len(mav_commands)):
    message = connection.mav.command_long_send(
            connection.target_system,  # Target system ID
            connection.target_component,  # Target component ID
            mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send
            0,  # Confirmation
            mav_commands[i],  # param1: Message ID to be streamed
            (1/refresh_rate_global)*10**6, # param2: Interval in microseconds. (1/f)=T. Seconds to microseconds is 10**6
            0, 0, 0, 0, 
            0  # target address
            )
```

There are two main ways we can set a servo. The first one is writing the PWM value directly to the cube:
```python
def set_servo(enum, pwm_val):
    message = connection.mav.command_long_send(
            connection.target_system,  # Target system ID
            connection.target_component,  # Target component ID
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO,  # ID of command to send
            0,  # Confirmation
            enum,  # param1: Message ID to be streamed
            pwm_val, # param2: Interval in microseconds
            0, 0, 0, 0, 
            0  # target address
            )
```
And the second method being sending a manual control message which overrides the channels:
```python
    connection.mav.manual_control_send(connection.target_system,
        int(-input_commands['elevator'] * 1000),
        int(input_commands['aileron'] * 1000),
        1000,
        0,
        0
    )
```

The UI script is rather straightforward and does not involve complex logics such as on the main mavlink script which needs a lot of care.
# Ivan feel free to do your doc below

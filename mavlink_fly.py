from pymavlink import mavutil

connection = mavutil.mavlink_connection('tcp:127.0.0.1:5762')

connection.wait_heartbeat()

connection.mav.command_long_send(connection.target_system,connection.target_component,mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,0,1,0,0,0,0,0,0)

print("Waiting for the vehicle to arm")
connection.motors_armed_wait()
print('Armed')

mode = 'TAKEOFF'

# Check if mode is available
if mode not in connection.mode_mapping():
    print('Unknown mode : {}'.format(mode))
    print('Try:', list(connection.mode_mapping().keys()))
    sys.exit(1)

# Get mode ID
mode_id = connection.mode_mapping()[mode]
# Set new mode
# master.mav.command_long_send(
#    master.target_system, master.target_component,
#    mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
#    0, mode_id, 0, 0, 0, 0, 0) or:
# master.set_mode(mode_id) or:
connection.mav.set_mode_send(
    connection.target_system,
    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
    mode_id)

while True:
    # Wait for ACK command
    # Would be good to add mechanism to avoid endlessly blocking
    # if the autopilot sends a NACK or never receives the message
    ack_msg = connection.recv_match(type='COMMAND_ACK', blocking=True)
    ack_msg = ack_msg.to_dict()

    # Continue waiting if the acknowledged command is not `set_mode`
    if ack_msg['command'] != mavutil.mavlink.MAV_CMD_DO_SET_MODE:
        continue

    # Print the ACK result !
    print(mavutil.mavlink.enums['MAV_RESULT'][ack_msg['result']].description)
    break

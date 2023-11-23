#Elmo arm disarm

from pymavlink import mavutil

connection = mavutil.mavlink_connection('tcp:127.0.0.1:5762')

connection.wait_heartbeat()

connection.mav.command_long_send(connection.target_system,connection.target_component,mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,0,1,0,0,0,0,0,0)

print("Waiting for the vehicle to arm")
connection.motors_armed_wait()
print('Armed')


connection.mav.command_long_send(connection.target_system,connection.target_component,mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,0,0,0,0,0,0,0,0)
connection.motors_disarmed_wait()
print('Disarmed!')

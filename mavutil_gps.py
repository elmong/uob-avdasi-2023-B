import time 
from pymavlink import mavutil

master = mavutil.mavlink_connection('tcp:127.0.0.1:5762')

master.wait_heartbeat()
print('connected')
while True:
    time.sleep(0.01)
    master.mav.gps_input_send(0,0,(mavutil.mavlink.GPS_INPUT_IGNORE_FLAG_VEL_HORIZ|mavutil.mavlink.GPS_INPUT_IGNORE_FLAG_VEL_VERT|mavutil.mavlink.GPS_INPUT_IGNORE_FLAG_SPEED_ACCURACY),0,0,3,0,0,0,1,1,0,0,0,0,0,0,7)
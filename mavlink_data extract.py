from pymavlink import mavutil
import numpy as np

roll = 0

port='com5' # simulator 'tcp:127.0.0.1:5762' , cube com#

connection = mavutil.mavlink_connection(port) #connect to local simulator, change to com'number' 

connection.wait_heartbeat() #heartbeat so make sure it's connected to the flight controller


while True:
    msg=connection.recv_match()

    if not msg:
        continue
    if msg.get_type() == 'ATTITUDE': #get type of message , check mavlink inspector on missionplanner to get type.
        attitude=msg.to_dict() #extract message to dictionary
        print(attitude)
        
        
        yaw=attitude['yaw'] #extract value from dictionary : so 'roll', 'pitch', 'yawspeed'
        print('yaw :' + str(yaw*180/np.pi) +' deg')
        pitch=attitude['pitch']
        print('pitch :' + str(pitch*180/np.pi) +' deg')
        roll=attitude['roll']
        print('roll :' + str(roll*180/np.pi) +' deg')


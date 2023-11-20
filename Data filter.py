from pymavlink import mavutil

# Create the connection
# From topside computer
master = mavutil.mavlink_connection('com5')

while True:
    msg = master.recv_match()
    if not msg:
        continue
    if msg.get_type() =='':
        print("\n\n*****Got message: %s*****" % msg.get_type())
        print("Message: %s" % msg)
        print("\nAs dictionary: %s" % msg.to_dict())
        print("\nSystem status: %s" % msg.system_status)
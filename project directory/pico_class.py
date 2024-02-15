import serial
import GCS_serial_reader
from global_var import *

#this is a class used to store and manipulate the picos' connection and its status
class Pico:
    
    #object instantiation
    def __init__(self, local_id, connection, connection_status, com_port, actual_id):
        #assign object attributes
        self.Local_ID = local_id #this ID does not have to match the actual pico's ID, but rather it is a local ID to keep track of objects
        self.Connection = connection
        self.Connection_status = connection_status
        self.COM_port = com_port
        self.Actual_id = actual_id #this is the actual ID of the pico

    def __str__(self): #returns object as a string
        return str(str(self.Local_ID) + str(self.Connection) + str(self.Connection_status) + str(self.COM_port) + str(self.Actual_id))

    #set actual id
    def ActualID(self,actual_id):
        self.Actual_id = actual_id

    #attempt to open the connection
    def initialize_connection(self):
        try:    
            self.COM_port = coms_ports['pico'+str(self.Local_ID)]
            Pico_serial_connection = serial.Serial(self.COM_port) # opens the connection
            self.Connection = Pico_serial_connection
            self.Connection_status = True
            print('Connection opened on ' + self.COM_port)
            
        except:
            self.Connection_status = False
            print("Connection failed on " + str(self.COM_port))
   
        # Pico_serial_connection = serial.Serial(self.COM_port) # opens the connection
        # self.Connection = Pico_serial_connection
        # self.Connection_status = True

    def close_connection(self):
        if self.Connection_status == True:
            self.Connection.close()
            self.Connection_status = False
            print('Connection closed on ' + self.COM_port)

         

    def read_message(self):
        try:
            self.Actual_id = GCS_serial_reader.ReadSerialMessage(self.Connection)
        except:
            self.Connection_status = False
        
        
        #self.Actual_id = GCS_serial_reader.ReadSerialMessage(self.Connection)
        
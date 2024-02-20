import os
import dictionary_dumper
from global_var import *

def GCS_BEGIN_PROGRAM():
    loaded_list = dictionary_dumper.load()
    if loaded_list is not None:
        print(loaded_list)
        global PID_values, coms_ports
        PID_values, coms_ports = loaded_list # FIXME this line is clearly not working
    print("GLOBAL FUNCTION: GCS STARTUP")

def GCS_EXIT_PROGRAM():
    list_to_be_saved = [PID_values, coms_ports]
    for dictionary in list_to_be_saved:
        print(dictionary)
    dictionary_dumper.save(list_to_be_saved)
    print("GLOBAL FUNCTION: GCS SHUTDOWN")
    os._exit(os.EX_OK)
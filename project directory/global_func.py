import os
import dictionary_dumper
from global_var import *

def GCS_BEGIN_PROGRAM():
    loaded_list = dictionary_dumper.load()
    if loaded_list is not None:
        if len(loaded_list) == 4: # remember to modify this val
            a, b, c, d = loaded_list
            for k, v in a.items():
                PID_values[k] = a[k]
            for k, v in b.items():
                coms_ports[k] = b[k]
            for k, v in c.items():
                input_commands[k] = c[k]
            for k, v in d.items():
                for k2, v2 in d[k].items():
                    control_surfaces[k][k2] = d[k][k2]
            print('***********GLOBAL VAR LOADED SUCCESSFULLY***********')
        else:
            print('***********LIST MISMATCH, JSON NOT LOADED***********')
    else:
        print('***********JSON NOT LOADED, FILE DOES NOT EXIST***********')
    print("***********GLOBAL FUNCTION: GCS STARTUP***********")

def GCS_EXIT_PROGRAM(list_to_be_saved): # pass the list through!
    for dictionary in list_to_be_saved:
        print(dictionary)
    dictionary_dumper.save(list_to_be_saved)
    print("***********GLOBAL FUNCTION: GCS SHUTDOWN***********")
    os._exit(os.EX_OK)
import os
import dictionary_dumper
from global_var import *

def GCS_BEGIN_PROGRAM():
    print("GLOBAL FUNCTION: GCS STARTUP")
    # TODO add dictionary load

def GCS_EXIT_PROGRAM():
    # TODO add dictionary save
    print("GLOBAL FUNCTION: GCS SHUTDOWN")
    os._exit(os.EX_OK)
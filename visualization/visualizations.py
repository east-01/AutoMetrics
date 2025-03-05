import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.dates as mdates
import datetime
from dotenv import load_dotenv,find_dotenv
print("Current Working Directory:", os.getcwd())
load_dotenv()
find_dotenv()


#Helper functions
existing_uid = set()
def find_uid(text):
    start_pos = text.find('uid=')

# Check if 'uid=' is found in the string|
    if start_pos != -1:
        # Adjust start_pos to point to the beginning of the uid value
        start_pos += len('uid=')
        
        # Find the position of the next comma after uid value
        end_pos = text.find(',', start_pos)
        
        # If there's no comma, go till the end of the string
        if end_pos == -1:
            end_pos = len(text)
        
        # Extract the uid value (removing quotes around it)
        uid_value = text[start_pos:end_pos].strip('"')
        return uid_value
    else:
        print("there's no uid")
        print(text)
        return None

#function to return True if a duplicate is found in gpu_set otherwise False
def is_not_duplicate(text, existing_uid):
    uid = find_uid(text)
    if uid not in existing_uid:
        existing_uid.add(uid)
        return True
    else:
        return False

#create a function that returns false if it in the list and true if it is not
def is_not_duplicate_and_not_a_gpu_job(text, existing_uid,common_uids):
    uid = find_uid(text)
    # if uid is in common_uids, return False as it is a GPU job, else it is a CPU-only job
    
    assert uid, "uid should be exist"
    if uid in common_uids:
        return False
    if uid in existing_uid:
        return False
    else:
        existing_uid.add(uid)
        return True
    


import os
import sys
import time
import random

try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
    from sumolib import checkBinary
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")
	
import traci

tls_id = 'ltk32_e10_0'

def get_test():
    tls_state = traci.getLastStepVehicleNumber(tls_id)
    print(tls_state)

def printMyname():
	print("Ngo Van Tai")

def set_params(self, entries):
        global turn_left, turn_right, turn_straight, fields, ltk_green, lgtht_green, set_phase_ltk, set_phase_lgtht
        
        
        self.set_phase_ltk = True
        self.set_phase_lgtht = True
        
        for entry in entries:
            if (entry[0] == self.fields[0] and self.is_int(entry[1].get())):
                self.red_light = entry[1].get()
            elif (entry[0] == self.fields[1] and self.is_int(entry[1].get())):
                self.ltk_green = entry[1].get()
            elif (entry[0] == self.fields[2] and self.is_int(entry[1].get())):
                self.lgtht_green = entry[1].get()
                
        print("+ red light : ",int(self.red_light))
        print("+ ltk green : ",self.ltk_green)
        print("+ lgtht green : ",self.lgtht_green)
	
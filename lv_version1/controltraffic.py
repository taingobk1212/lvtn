from __future__ import absolute_import
from __future__ import print_function

import traci
from Tkinter import *;
from threading import Thread
import os
import sys
import optparse
import subprocess
import random
from cProfile import label
from Tix import AUTO
import optimize
from PIL import ImageTk, Image

# we need to import python modules from the $SUMO_HOME/tools directory
try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
    from sumolib import checkBinary
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

class Application(Frame): 
    set_phase_ltk = False
    set_phase_lgtht = False
    fields = 'Red tl Violation Rate', 'Green tl cycle of Ly Thuong Kiet', 'Green tl cycle of Lu Gia - To Hien Thanh'
    
    #params ( value : percent)
    red_light = 0
    turn_left = 0
    turn_right = 0
    turn_straight = 0
    ltk_green = 0
    lgtht_green = 0
    
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent        
        self.initUI()
        
    def get_options(self):
        optParser = optparse.OptionParser()
        optParser.add_option("--nogui", action="store_true",
                             default=False, help="run the commandline version of sumo")
        options, args = optParser.parse_args()
        return options
    
    def start_sumo_thread(self):
        thread = Thread(target = self.start_sumo)
        thread.start()
        print("start thread sumo")
        
    def stop_sumo(self):
        traci.close()
    
    def run_sumo(self):       
        global set_phase_ltk, set_phase_lgtht
        traci.switch("sumovn")       
        """execute the TraCI control loop"""
        print('running')
        step = 0
        while traci.simulation.getMinExpectedNumber() > 0:                  
            traci.simulationStep()
            
            #listVehicleId = traci.vehicle.getIDList()
            #print(listVehicleId)
            #set phase tls
            phase = traci.trafficlights.getPhase("ltk_intersection")
            if (self.set_phase_ltk == True and phase == 0 and int(self.ltk_green) > 10): 
                old_ltk_green = traci.trafficlights.getPhaseDuration("ltk_intersection")
                print(old_ltk_green)
                if(int(self.ltk_green) != int(old_ltk_green)):
                    traci.trafficlights.setPhaseDuration("ltk_intersection", int(self.ltk_green))
                    self.set_phase_ltk = False
                    print("success ltk: ",self.ltk_green)
                   
            if (self.set_phase_lgtht == True and phase == 2 and int(self.lgtht_green) > 10): 
                old_lgtht_green = traci.trafficlights.getPhaseDuration("ltk_intersection")
                if(int(self.lgtht_green) != int(old_lgtht_green)):
                    traci.trafficlights.setPhaseDuration("ltk_intersection", int(self.lgtht_green)) 
                    self.set_phase_lgtht = False
                    print("success lgtht: ",self.lgtht_green)               
            step += 1            
        traci.close()
        sys.stdout.flush() 
        
    def start_sumo(self):        
        options = self.get_options()      
        if options.nogui:
            sumoBinary = checkBinary('sumo')
        else:
            sumoBinary = checkBinary('sumo-gui')
        
        sumoCmd = [sumoBinary, "-c", "maps/map.sumo.cfg", "--time-to-teleport", "60", "--lateral-resolution", "0.9"]
        traci.start(sumoCmd, label="sumovn")
        self.run_sumo()
        
   
    def makeform(self,root, fields):
        entries = []
        for field in fields:
            row = Frame(root)
            lab = Label(row, width=30, text=field, anchor='w')
            ent = Entry(row)
            
            row.pack(side=TOP, fill=X, padx=5, pady=5)
            lab.pack(side=LEFT)
            ent.pack(side=RIGHT, expand=YES, fill=X)
            entries.append((field, ent))
        return entries
   
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
        
    def is_int(self, value):
        try:
            int(value)
            return True
        except:
            return False    
           
    def initUI(self):
        self.parent.title("Traffic Controller")
        fieldsCon = 'Host', 'Port'
        #Field
        entries = []
        for field in fieldsCon:
            row = Frame(root)
            lab = Label(row, width=10, text=field, anchor='w')
            ent = Entry(row)
           
            row.pack(side=TOP, fill=X, padx=5, pady=5)
            lab.pack(side=LEFT)
            ent.pack(side=RIGHT, expand=YES, fill=X)
            entries.append((field, ent))
         
        frame = Frame(self, relief=RAISED, borderwidth=1)
        frame.pack(fill=BOTH, expand=True)
        self.pack(fill=BOTH, expand=True)
        connectButton = Button(self, text="Connect", bg ='green', command = self.quit)     
        connectButton.pack(side=LEFT, padx=5, pady=5)
        closeButton = Button(self, text="Close", command = self.quit)
        closeButton.pack(side=RIGHT, padx=5, pady=5)
        
        startSumoButton = Button(self, text="Start Sumo", command = self.start_sumo_thread)
        startSumoButton.pack(side=RIGHT)  
     
        bottom_button = Frame(self.parent);
        # submitbtn
        entries = self.makeform(self.parent, self.fields)
        self.master.bind('<Return>', (lambda event, e=entries: self.set_params(e)))
        self.submitBtn = Button(bottom_button, text='Set Params', fg='black', bg ='yellow', command=(lambda e=entries: self.set_params(e)))
        
        bottom_button.pack(side=BOTTOM, fill=X, padx=5, pady=5)
        self.submitBtn.pack(side=LEFT)
 
root = Tk()
#root.geometry("300x200+300+300")
app = Application(root)
root.mainloop()
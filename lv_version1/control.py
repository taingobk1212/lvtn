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
    print("create")
    fields = 'Red tl Violation Rate', 'Green Light Ly Thuong Kiet', 'Green Light Lu Gia - To Hien Thanh'
    fieldsCon = 'Host', 'Port'   
    
    def start_sumo_thread(self):
        thread = Thread(target = self.start_sumo)
        thread.start()
        print("start thread sumo")
        
    def stop_sumo(self):
        traci.close()    
    
    def start_sumo(self):        
        sumoCmd = ["sumo-gui", "-c", "maps/map.sumo.cfg", "--time-to-teleport", "60", "--lateral-resolution", "0.9"]
        traci.start(sumoCmd, label="sumovn")
        self.run_sumo()
        
    def run_sumo(self):
        global set_phase_ltk, set_phase_lgtht
        traci.switch("sumovn")       
        """execute the TraCI control loop"""
        print('running')
        step = 0
        while traci.simulation.getMinExpectedNumber() > 0:
            print(traci.simulation.getMinExpectedNumber())
            traci.simulationStep()            
            step += 1            
        traci.close()
        sys.stdout.flush()    
    
    def optimizeTraffic(self):
        optimize.get_test()
        
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
    
    def makeformConnect(self,root, fieldsCon):        
        entries = []
        for field in fieldsCon:
            row = Frame(root)
            lab = Label(row, width=30, text=field, anchor='w')
            ent = Entry(row)
            
            row.pack(side=TOP, fill=X, padx=5, pady=5)
            lab.pack(side=LEFT)
            ent.pack(side=RIGHT, expand=YES, fill=X)
            entries.append((field, ent))
        return entries
    
    def createWidgetsConnect(self):  
        self.winfo_toplevel().title("TraCI SUMO Controller")
        #Connect to server
        self.connectBtn = Button(self, text='Connect', fg='blue', command = self.createWidgets)     
        self.connectBtn.pack()
        entries = self.makeformConnect(self.master, self.fieldsCon)   
    
    def createWidgets(self):
        optimize.printMyname()        
        # hide button      
        self.connectBtn.pack_forget()       
        self.winfo_toplevel().title("TraCI SUMO Controller")           
        # start sumo
        self.startSumoBtn = Button(self, text='Start Sumo', fg='black', command = self.start_sumo_thread)      
        # Optimize AutoTrafficLight
        self.optimizeBtn = Button(self, text='Optomize', fg='black', command = self.optimizeTraffic)  
        # quit app
        self.quitAppBtn = Button(self, text='Quit', fg='red', command = self.quit)        
        
        entries = self.makeform(self.master, self.fields)        
        ######
        self.startSumoBtn.pack(side=LEFT, padx=5, pady=5)
        self.optimizeBtn.pack(side=LEFT, padx=5, pady=5)
        self.quitAppBtn.pack(side=LEFT, padx=5, pady=5)        
    def __init__(self, master=None):
        master.resizable(width=False, height=False)
        #master.minsize(width=600, height=400)
        #master.maxsize(width=600, height=400)
        Frame.__init__(self, master)
        self.pack()
        self.createWidgetsConnect()
        
root = Tk();
app = Application(master=root)
app.mainloop()
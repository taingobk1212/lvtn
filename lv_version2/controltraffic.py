from __future__ import absolute_import
from __future__ import print_function

import traci
from Tkinter import *
from threading import Thread , Timer
import os
import sys
import optparse
import subprocess
import random
from cProfile import label
from Tix import AUTO
import optimize
from PIL import ImageTk, Image
import requests
import socket
import threading
import json
import intersection

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
    HOST = '127.0.0.1'
    PORT = '8000'
    isfirst = False
    connected = False
    issetparams = False
    set_phase_ltkhvt = False
    set_phase_tccmt8 = False
    fields = 'Green tl cycle of Ly Thuong Kiet - Hoang Van Thu', 'Green tl cycle of Truong Chinh - CMT8'
    
    #params ( value : percent)    
    ltkhvt_green = 0
    tccmt8_green = 0

    # value info intersection
    list_vehicle_ltk = []
    list_vehicle_tc = []
    list_vehicle_cmt8 = []

    list_vehiclepass_ltk = []
    list_vehiclepass_cmt8 = []
    list_vehiclepass_hvt = []

    nVhccome_ltk = 0
    nVhccome_cmt8 = 0
    nVhccome_tr = 0

    nVhcpass_ltk = 0
    nVhcpass_cmt8 = 0
    nVhcpass_hvt = 0

    ftccmt8_green = 0
    fltkhvt_green = 0
    ftccmt8_yellow = 0
    fltkhvt_yellow = 0
    
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
        global set_phase_ltkhvt, set_phase_tccmt8, connected, HOST, PORT     
        traci.switch("sumovn")       
        """execute the TraCI control loop"""
        print('running')   
        httphost_putdetails = 'http://'+self.HOST+':'+self.PORT+'/home/puttldatadetails' 
        httphost_get = 'http://'+self.HOST+':'+self.PORT+'/home/gettldata'  
        httphost_put = 'http://'+self.HOST+':'+self.PORT+'/home/puttldata'   
        httphost_puttl = 'http://'+self.HOST+':'+self.PORT+'/home/puttrafficlightdata' 
        step = 0
        putdatadetail = False
        while traci.simulation.getMinExpectedNumber() > 0:                  
            traci.simulationStep()                                         

            self.countVehicleCome(traci.inductionloop.getIDList())
            if (int(traci.simulation.getTime())%181) == 0:
                putdatadetail = False
            if (int(traci.simulation.getTime())%180) == 0 and int(traci.simulation.getTime()):   
                print("Vehicle come 3 minute ago")                  
                result_ltk = self.queueVehicleLength_ltk()          
                result_cmt8 = self.queueVehicleLength_cmt8()   
                result_tc = self.queueVehicleLength_tc() 

                vtb_ltk = (traci.lane.getLastStepMeanSpeed("ltk_e2_0") + traci.lane.getLastStepMeanSpeed("ltk_e2_1"))/2
                vtb_cmt8 = (traci.lane.getLastStepMeanSpeed("cmt8_e2_0") + traci.lane.getLastStepMeanSpeed("cmt8_e2_1"))/2
                vtb_tc = (traci.lane.getLastStepMeanSpeed("tc_e2_0") + traci.lane.getLastStepMeanSpeed("tc_e2_1"))/2  
                vtb_hvt = (traci.lane.getLastStepMeanSpeed("hvt_e2_0") + traci.lane.getLastStepMeanSpeed("hvt_e2_1") + traci.lane.getLastStepMeanSpeed("hvt_e5_0") + traci.lane.getLastStepMeanSpeed("hvt_e5_1"))/4 
                print("ltk come: ", len(self.list_vehicle_ltk))
                print("tc come: ", len(self.list_vehicle_tc))
                print("cmt8 come: ", len(self.list_vehicle_cmt8))              
                
                print("ltk pass: ", len(self.list_vehiclepass_ltk))
                print("hvt pass: ", len(self.list_vehiclepass_hvt))
                print("cmt8 pass: ", len(self.list_vehiclepass_cmt8))  
                
                if (self.connected == True and putdatadetail == False):
                    try:
                        putdatadetail = True
                        info = {'id':'bayhien','apprid1':'bayhien_ltk', 'apprid2':'bayhien_cmt8', 'apprid3':'bayhien_tc','apprid4':'bayhien_hvt','vhccome1': len(self.list_vehicle_ltk), 'vhccome2': len(self.list_vehicle_cmt8), 'vhccome3': len(self.list_vehicle_tc), 'vhccome4': 0, 'vhcout1': len(self.list_vehiclepass_ltk), 'vhcout2': len(self.list_vehiclepass_cmt8), 'vhcout3': 0,'vhcout4': len(self.list_vehiclepass_hvt), 'vtb1':vtb_ltk, 'vtb2': vtb_cmt8, 'vtb3': vtb_tc, 'vtb4': vtb_hvt, 'queue_length1': result_ltk[0], 'queue_length2': result_cmt8[0], 'queue_length3': result_tc[0], 'queue_length4': 0, 'waittime1': result_ltk[1], 'waittime2': result_cmt8[1], 'waittime3': result_tc[1], 'waittime4': 0}      
                        res = requests.get(httphost_putdetails, params = info)                    
                        self.connected = True                    
                    except:
                        self.connected = False                         
                        self.isfirst = True       
                        self.disconnectButton.configure(state=DISABLED)     
                        self.connectButton.configure(state=NORMAL)
                        print("connect fail")   

                self.list_vehicle_ltk = []
                self.list_vehicle_cmt8 = []
                self.list_vehicle_tc = []                    
                self.list_vehiclepass_ltk = []
                self.list_vehiclepass_cmt8 = []
                self.list_vehiclepass_hvt = []     


            if (self.connected == True and self.issetparams == False):
                try:
                    info = {'id':'bayhien'}      
                    res = requests.get(httphost_get, params = info)                     
                    self.connected = True                    
                except:
                    self.connected = False                    
                    self.isfirst = True       
                    self.disconnectButton.configure(state=DISABLED)     
                    self.connectButton.configure(state=NORMAL)
                    print("connect fail") 

                if (self.connected == True):
                    if (res.json()['isparams'] == 'True'):                            
                        print("set params")
                        self.set_phase_tccmt8 = True
                        self.set_phase_ltkhvt = True   
                        # print(len(res.json()['trafficlight']))
                        for i in range(len(res.json()['trafficlight'])):                      
                            if (res.json()['trafficlight'][i]['apprid'] == 'tc_cmt8'):
                                self.tccmt8_green = res.json()['trafficlight'][i]['tlgreen']
                            if (res.json()['trafficlight'][i]['apprid'] == 'ltk_hvt'):
                                self.ltkhvt_green = res.json()['trafficlight'][i]['tlgreen']

                        info = {'id':'bayhien','bparams': False}   
                        res = requests.get(httphost_put, params = info)
                
            phase = traci.trafficlights.getPhase("bayhien_intersection")   

            global ftccmt8_green, fltkhvt_green, ftccmt8_yellow, fltkhvt_yellow
            if (self.isfirst == True and self.connected == True):               
                if (phase == 0):
                    self.ftccmt8_green = int(traci.trafficlights.getPhaseDuration("bayhien_intersection"))
                if (phase == 1):
                    self.ftccmt8_yellow = int(traci.trafficlights.getPhaseDuration("bayhien_intersection"))
                if (phase == 2):  
                    self.fltkhvt_green = int(traci.trafficlights.getPhaseDuration("bayhien_intersection"))
                if (phase == 3):  
                    self.fltkhvt_yellow = int(traci.trafficlights.getPhaseDuration("bayhien_intersection"))
                # print("first",  self.ftccmt8_green, self.fltkhvt_green)    
                if (self.ftccmt8_green != 0 and self.fltkhvt_green != 0 and self.ftccmt8_yellow != 0 and self.fltkhvt_yellow != 0):    
                    info = {'id':'bayhien', 'apprid': 'tc_cmt8', 'tlgreen': self.ftccmt8_green, 'tlyellow': self.ftccmt8_yellow, 'tlred': self.fltkhvt_green}   
                    res = requests.get(httphost_puttl, params = info)
                    info = {'id':'bayhien', 'apprid': 'ltk_hvt', 'tlgreen': self.fltkhvt_green, 'tlyellow': self.fltkhvt_yellow, 'tlred': self.ftccmt8_green}
                    res = requests.get(httphost_puttl, params = info)
                    self.isfirst = False
                    print("put param to server")  
                    print(self.ftccmt8_green) 
                    print(self.fltkhvt_green)
                    self.ftccmt8_green = 0
                    self.fltkhvt_green = 0                    

            # print("normal")                    
            if (self.set_phase_tccmt8 == True and phase == 0 and int(self.tccmt8_green) > 10): 
                old_tccmt8_green = traci.trafficlights.getPhaseDuration("bayhien_intersection")                
                if(int(self.tccmt8_green) != int(old_tccmt8_green)):
                    traci.trafficlights.setPhaseDuration("bayhien_intersection", int(self.tccmt8_green))
                    self.set_phase_tccmt8 = False
                    print("success tccmt8: ",self.tccmt8_green)                   
                else:   
                    self.set_phase_tccmt8 = False  
                   
            if (self.set_phase_ltkhvt == True and phase == 2 and int(self.ltkhvt_green) > 10): 
                old_ltkhvt_green = traci.trafficlights.getPhaseDuration("bayhien_intersection")
                if(int(self.ltkhvt_green) != int(old_ltkhvt_green)):
                    traci.trafficlights.setPhaseDuration("bayhien_intersection", int(self.ltkhvt_green)) 
                    self.set_phase_ltkhvt = False
                    print("success ltkhvt: ",self.ltkhvt_green)       
                else:
                    self.set_phase_ltkhvt = False                    
            # print("step ",step)        
            step += 1            
        traci.close()
        sys.stdout.flush()    

    def queueVehicleLength_ltk(self):        
        numberVehicle = 0
        length_ltk = 0
        minpos_ltk = traci.lane.getLength("ltk_e1_0")
        # print(minpos_ltk)
        queue_ltk = traci.lane.getLastStepVehicleIDs("ltk_e1_0") + traci.lane.getLastStepVehicleIDs("ltk_e1_1")
        for vhcid in queue_ltk:
            if traci.vehicle.getSpeed(vhcid) <= 1.38:
                numberVehicle += 1
                if (minpos_ltk > traci.vehicle.getLanePosition(vhcid)):
                    minpos_ltk = traci.vehicle.getLanePosition(vhcid)
        length_ltk = traci.lane.getLength("ltk_e1_0") - minpos_ltk
        
        minpos_ltk = traci.lane.getLength(":ltk_junc1_3_0")
        # print(minpos_ltk)
        queue_ltk = traci.lane.getLastStepVehicleIDs(":ltk_junc1_3_0") + traci.lane.getLastStepVehicleIDs(":ltk_junc1_3_1")
        for vhcid in queue_ltk:
            if traci.vehicle.getSpeed(vhcid) <= 1.38:
                numberVehicle += 1
                if (minpos_ltk > traci.vehicle.getLanePosition(vhcid)):
                    minpos_ltk = traci.vehicle.getLanePosition(vhcid)
        if (traci.lane.getLength(":ltk_junc1_3_0") - minpos_ltk) > 0:            
            length_ltk =length_ltk + traci.lane.getLength(":ltk_junc1_3_0") - minpos_ltk

        minpos_ltk = traci.lane.getLength("ltk_e2_0")
        queue_ltk = traci.lane.getLastStepVehicleIDs("ltk_e2_0") + traci.lane.getLastStepVehicleIDs("ltk_e2_1")        
        for vhcid in queue_ltk:
            if traci.vehicle.getSpeed(vhcid) <= 1.38:
                numberVehicle += 1
                if (minpos_ltk > traci.vehicle.getLanePosition(vhcid)):
                    minpos_ltk = traci.vehicle.getLanePosition(vhcid)
        if (traci.lane.getLength("ltk_e2_0") - minpos_ltk) > 0:            
            length_ltk =length_ltk + traci.lane.getLength("ltk_e2_0") - minpos_ltk    

        total_wait_time = traci.lane.getWaitingTime("ltk_e1_0") + traci.lane.getWaitingTime("ltk_e1_1") + traci.lane.getWaitingTime("ltk_e2_0") + traci.lane.getWaitingTime("ltk_e2_1") + traci.lane.getWaitingTime(":ltk_junc1_3_0") + traci.lane.getWaitingTime(":ltk_junc1_3_1")   
        if numberVehicle > 0:
            wait_time_tb = total_wait_time / numberVehicle    
        else:
            wait_time_tb = 0  
        # print("LTK: ",length_ltk)  
        # print("Waitting time: ", wait_time_tb) 
        # print(numberVehicle)
        data = [length_ltk, wait_time_tb]
        return data 

    def queueVehicleLength_cmt8(self):        
        numberVehicle = 0
        length_cmt8 = 0
        minpos_cmt8 = traci.lane.getLength("cmt8_e1_0")
        # print(minpos_cmt8)
        queue_cmt8 = traci.lane.getLastStepVehicleIDs("cmt8_e1_0") + traci.lane.getLastStepVehicleIDs("cmt8_e1_1")
        for vhcid in queue_cmt8:
            if traci.vehicle.getSpeed(vhcid) <= 1.38:
                numberVehicle += 1
                if (minpos_cmt8 > traci.vehicle.getLanePosition(vhcid)):
                    minpos_cmt8 = traci.vehicle.getLanePosition(vhcid)
        length_cmt8 = traci.lane.getLength("cmt8_e1_0") - minpos_cmt8
        
        minpos_cmt8 = traci.lane.getLength(":cmt8_junc1_1_0")
        # print(minpos_cmt8)
        queue_cmt8 = traci.lane.getLastStepVehicleIDs(":cmt8_junc1_1_0") + traci.lane.getLastStepVehicleIDs(":cmt8_junc1_1_1")
        for vhcid in queue_cmt8:
            if traci.vehicle.getSpeed(vhcid) <= 1.38:
                numberVehicle += 1
                if (minpos_cmt8 > traci.vehicle.getLanePosition(vhcid)):
                    minpos_cmt8 = traci.vehicle.getLanePosition(vhcid)
        if (traci.lane.getLength(":cmt8_junc1_1_0") - minpos_cmt8) > 0:            
            length_cmt8 =length_cmt8 + traci.lane.getLength(":cmt8_junc1_1_0") - minpos_cmt8

        minpos_cmt8 = traci.lane.getLength("cmt8_e2_0")
        queue_cmt8 = traci.lane.getLastStepVehicleIDs("cmt8_e2_0") + traci.lane.getLastStepVehicleIDs("cmt8_e2_1")        
        for vhcid in queue_cmt8:
            if traci.vehicle.getSpeed(vhcid) <= 1.38:
                numberVehicle += 1
                if (minpos_cmt8 > traci.vehicle.getLanePosition(vhcid)):
                    minpos_cmt8 = traci.vehicle.getLanePosition(vhcid)
        if (traci.lane.getLength("cmt8_e2_0") - minpos_cmt8) > 0:            
            length_cmt8 =length_cmt8 + traci.lane.getLength("cmt8_e2_0") - minpos_cmt8    

        total_wait_time = traci.lane.getWaitingTime("cmt8_e1_0") + traci.lane.getWaitingTime("cmt8_e1_1") + traci.lane.getWaitingTime("cmt8_e2_0") + traci.lane.getWaitingTime("cmt8_e2_1") + traci.lane.getWaitingTime(":cmt8_junc1_1_0") + traci.lane.getWaitingTime(":cmt8_junc1_1_1")   
        if numberVehicle > 0:
            wait_time_tb = total_wait_time / numberVehicle    
        else:
            wait_time_tb = 0  
        # print("CMT8: ",length_cmt8)  
        # print("Waitting time: ", wait_time_tb) 
        data = [length_cmt8, wait_time_tb]
        return data

    def queueVehicleLength_tc(self):        
        numberVehicle = 0
        length_tc = 0
        minpos_tc = traci.lane.getLength("tc_e3_0")
        # print(minpos_tc)
        queue_tc = traci.lane.getLastStepVehicleIDs("tc_e3_0") + traci.lane.getLastStepVehicleIDs("tc_e3_1") + traci.lane.getLastStepVehicleIDs("tc_e3_2")
        for vhcid in queue_tc:
            if traci.vehicle.getSpeed(vhcid) <= 1.38:
                numberVehicle += 1
                if (minpos_tc > traci.vehicle.getLanePosition(vhcid)):
                    minpos_tc = traci.vehicle.getLanePosition(vhcid)
        length_tc = traci.lane.getLength("tc_e3_0") - minpos_tc
        
        minpos_tc = traci.lane.getLength(":tc_junc1_1_0")
        # print(minpos_tc)
        queue_tc = traci.lane.getLastStepVehicleIDs(":tc_junc1_1_0") + traci.lane.getLastStepVehicleIDs(":tc_junc1_1_1") + traci.lane.getLastStepVehicleIDs(":tc_junc1_1_2")
        for vhcid in queue_tc:
            if traci.vehicle.getSpeed(vhcid) <= 1.38:
                numberVehicle += 1
                if (minpos_tc > traci.vehicle.getLanePosition(vhcid)):
                    minpos_tc = traci.vehicle.getLanePosition(vhcid)
        if (traci.lane.getLength(":tc_junc1_1_0") - minpos_tc) > 0:            
            length_tc =length_tc + traci.lane.getLength(":tc_junc1_1_0") - minpos_tc

        minpos_tc = traci.lane.getLength("tc_e2_0")
        queue_tc = traci.lane.getLastStepVehicleIDs("tc_e2_0") + traci.lane.getLastStepVehicleIDs("tc_e2_1") + traci.lane.getLastStepVehicleIDs("tc_e2_2")       
        for vhcid in queue_tc:
            if traci.vehicle.getSpeed(vhcid) <= 1.38:
                numberVehicle += 1
                if (minpos_tc > traci.vehicle.getLanePosition(vhcid)):
                    minpos_tc = traci.vehicle.getLanePosition(vhcid)
        if (traci.lane.getLength("tc_e2_0") - minpos_tc) > 0:            
            length_tc =length_tc + traci.lane.getLength("tc_e2_0") - minpos_tc    

        total_wait_time = traci.lane.getWaitingTime("tc_e3_0") + traci.lane.getWaitingTime("tc_e3_1") + traci.lane.getWaitingTime("tc_e3_2") + traci.lane.getWaitingTime("tc_e2_0") + traci.lane.getWaitingTime("tc_e2_1") + traci.lane.getWaitingTime("tc_e2_2") + traci.lane.getWaitingTime(":tc_junc1_1_0") + traci.lane.getWaitingTime(":tc_junc1_1_1") + traci.lane.getWaitingTime(":tc_junc1_1_2")   
        if numberVehicle > 0:
            wait_time_tb = total_wait_time / numberVehicle    
        else:
            wait_time_tb = 0  
        # print("TC: ",length_tc)  
        # print("Waitting time: ", wait_time_tb) 
        # print(numberVehicle)
        data = [length_tc, wait_time_tb]
        return data

    def countVehicleCome(self, listInductionLoopId):
        global list_vehicle_ltk, list_vehicle_tc, list_vehicle_cmt8, list_vehiclepass_ltk, list_vehiclepass_cmt8, list_vehiclepass_hvt
        nvhc_ltk = []       
        nvhc_cmt8 = []
        nvhc_tc = []

        nvhc_pass_ltk = []       
        nvhc_pass_cmt8 = []
        nvhc_pass_hvt = []

        for inductionLoopId in listInductionLoopId:
            #count vehicle come
            if 'ltk_detector' in inductionLoopId:                  
                nvhc_ltk = traci.inductionloop.getLastStepVehicleIDs(inductionLoopId)               
                for vehicleId in nvhc_ltk:
                    if (self.list_vehicle_ltk.count(vehicleId) == 0):
                        self.list_vehicle_ltk.append(vehicleId)                       

            if 'cmt8_detector' in inductionLoopId:             
                nvhc_cmt8 = traci.inductionloop.getLastStepVehicleIDs(inductionLoopId)  
                for vehicleId in nvhc_cmt8:
                    if (self.list_vehicle_cmt8.count(vehicleId) == 0):
                        self.list_vehicle_cmt8.append(vehicleId)

            if 'tc_detector' in inductionLoopId:             
                nvhc_tc = traci.inductionloop.getLastStepVehicleIDs(inductionLoopId) 
                for vehicleId in nvhc_tc:
                    if (self.list_vehicle_tc.count(vehicleId) == 0):
                        self.list_vehicle_tc.append(vehicleId)

            # count vehicle pass     
            if 'ltk_pass_detector' in inductionLoopId:             
                nvhc_pass_ltk = traci.inductionloop.getLastStepVehicleIDs(inductionLoopId)     
                for vehicleId in nvhc_pass_ltk:
                    if (self.list_vehiclepass_ltk.count(vehicleId) == 0):
                        self.list_vehiclepass_ltk.append(vehicleId)
            # print(inductionLoopId)                        
            # print("ltkbd pass: ", len(self.list_vehiclepass_ltkbd))

            if 'cmt8_pass_detector' in inductionLoopId:             
                nvhc_pass_cmt8 = traci.inductionloop.getLastStepVehicleIDs(inductionLoopId)     
                for vehicleId in nvhc_pass_cmt8:
                    if (self.list_vehiclepass_cmt8.count(vehicleId) == 0):
                        self.list_vehiclepass_cmt8.append(vehicleId)

            if 'hvt_pass_detector' in inductionLoopId:             
                nvhc_pass_hvt = traci.inductionloop.getLastStepVehicleIDs(inductionLoopId)     
                for vehicleId in nvhc_pass_hvt:
                    if (self.list_vehiclepass_hvt.count(vehicleId) == 0):
                        self.list_vehiclepass_hvt.append(vehicleId)                          

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
            lab = Label(row, width=40, text=field, anchor='w')
            ent = Entry(row)
            
            row.pack(side=TOP, fill=X, padx=5, pady=5)
            lab.pack(side=LEFT)
            ent.pack(side=RIGHT, expand=YES, fill=X)
            entries.append((field, ent))
        return entries
   
    def set_params(self, entries):
        global fields, ltkhvt_green, tccmt8_green, set_phase_ltkhvt, set_phase_tccmt8        
        
        self.set_phase_ltkhvt = True
        self.set_phase_tccmt8 = True
        
        for entry in entries:
            if (entry[0] == self.fields[0] and self.is_int(entry[1].get())):
                self.ltkhvt_green = entry[1].get()
            elif (entry[0] == self.fields[1] and self.is_int(entry[1].get())):
                self.tccmt8_green = entry[1].get()            
        self.issetparams = True
        print("+ tccmt8 green : ",self.tccmt8_green)
        print("+ ltkhvt green : ",self.ltkhvt_green)
        
    def is_int(self, value):
        try:
            int(value)
            return True
        except:
            return False        

    def connectserver(self): 
        global HOST, PORT       
        try:
            # get ip lan wireless 
            self.HOST = socket.gethostbyname_ex(socket.gethostname())[2][3]            
            info = {'id':'ltk_lg'}      
            res = requests.get('http://'+self.HOST+':'+self.PORT+'/home/gettldata', params = info)              
            # print(res.status_code)   
            if (res.status_code == 200):
                print("Connected server by " + self.HOST)      
                self.connected = True
                self.isfirst = True
                self.disconnectButton.configure(state=NORMAL)     
                self.connectButton.configure(state=DISABLED)  
            else:
                print("Connect fail") 
                self.connected = False  
                self.isfirst = True               
        except:
            print("Connect fail") 
            self.connected = False  
            self.isfirst = True 

    def disconnect(self):                      
        self.connected = False 
        self.isfirst = True       
        self.disconnectButton.configure(state=DISABLED)     
        self.connectButton.configure(state=NORMAL)

    def initUI(self):
        self.parent.title("Traffic Controller")        
        frame = Frame(self, relief=RAISED, borderwidth=1)
        frame.pack(fill=BOTH, expand=True)
        self.pack(fill=BOTH, expand=True)
        self.connectButton = Button(self, text="Connect", bg ='green', command = self.connectserver)     
        self.connectButton.pack(side=LEFT, padx=5, pady=5)
        self.disconnectButton = Button(self, text="Disconnect",state=DISABLED ,bg ='green', command = self.disconnect)     
        self.disconnectButton.pack(side=LEFT, padx=5, pady=5)
        closeButton = Button(self, text="Close", command = self.quit)
        closeButton.pack(side=RIGHT, padx=5, pady=5)
        
        startSumoButton = Button(self, text="Start Sumo", command = self.start_sumo_thread)
        startSumoButton.pack(side=RIGHT)  
        bottom_button = Frame(self.parent)
        # submitbtn
        entries = self.makeform(self.parent, self.fields)
        self.master.bind('<Return>', (lambda event, e=entries: self.set_params(e)))
        self.submitBtn = Button(bottom_button, text='Set Params', fg='black', bg ='yellow', command=(lambda e=entries: self.set_params(e)))
        
        bottom_button.pack(side=BOTTOM, fill=X, padx=5, pady=5)
        self.submitBtn.pack(side=LEFT)
 
root = Tk()
app = Application(root)
root.mainloop()
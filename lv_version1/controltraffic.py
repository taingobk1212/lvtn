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
    set_phase_ltk = False
    set_phase_lgtht = False
    fields = 'Green tl cycle of Ly Thuong Kiet', 'Green tl cycle of Lu Gia - To Hien Thanh'
    
    #params ( value : percent)
    red_light = 0
    turn_left = 0
    turn_right = 0
    turn_straight = 0
    ltk_green = 0
    lgtht_green = 0
    fltk_green = 0
    flgtht_green = 0

    # value info intersection

    list_vehicle_ltkbd = []
    list_vehicle_ltkntd = []
    list_vehicle_lg = []
    list_vehicle_tht = []

    list_vehiclepass_ltkbd = []
    list_vehiclepass_ltkntd = []
    list_vehiclepass_lg = []
    list_vehiclepass_tht = []

    nVhccome_ltkbd = 0
    nVhccome_ltkntd = 0
    nVhccome_lg = 0
    nVhccome_tht = 0

    nVhcpass_ltkbd = 0
    nVhcpass_ltkntd = 0
    nVhcpass_lg = 0
    nVhcpass_tht = 0
    
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
        global set_phase_ltk, set_phase_lgtht, connected, isfirst, issetparams, HOST, PORT
        global list_vehicle_ltkbd, list_vehicle_ltkntd, list_vehicle_lg, list_vehicle_tht
        traci.switch("sumovn")       
        """execute the TraCI control loop"""
        print('running')
        httphost_get = 'http://'+self.HOST+':'+self.PORT+'/home/gettldata' 
        httphost_put = 'http://'+self.HOST+':'+self.PORT+'/home/puttldata' 
        httphost_putdetails = 'http://'+self.HOST+':'+self.PORT+'/home/puttldatadetails' 
        step = 0
        putdatadetail = False
        while traci.simulation.getMinExpectedNumber() > 0:                  
            traci.simulationStep()          

            #list vehicle in lane
            # print(traci.lane.getLastStepVehicleIDs("ltk32_e10_1"))    
            self.queueVehicleLength_ltkntd()    
            self.queueVehicleLength_ltkbd() 
            self.queueVehicleLength_lg() 
            self.queueVehicleLength_tht()

            if (int(traci.simulation.getTime())%181) == 0:
                putdatadetail = False

            if (int(traci.simulation.getTime())%180) == 0 and int(traci.simulation.getTime()) > 0 and putdatadetail == False:   
                print("Vehicle come 3 minute ago")             
                print("lg come: ", len(self.list_vehicle_lg))
                print("tht come: ", len(self.list_vehicle_tht))
                print("ltkbd come: ", len(self.list_vehicle_ltkbd))
                print("ltkntd come: ", len(self.list_vehicle_ltkntd))
                
                print("ltkbd pass: ", len(self.list_vehiclepass_ltkbd))
                print("ltkntd pass: ", len(self.list_vehiclepass_ltkntd))
                print("lg pass: ", len(self.list_vehiclepass_lg))
                print("tht pass: ", len(self.list_vehiclepass_tht))

                print(putdatadetail)    
                # clear list after 3 minute                                
                if (self.connected == True and  putdatadetail == False):                    
                    # tinh van toc trung binh
                    vtb_ltkntd = (traci.lane.getLastStepMeanSpeed("ltk32_e10_0") + traci.lane.getLastStepMeanSpeed("ltk32_e10_1"))/2
                    vtb_ltkbd = (traci.lane.getLastStepMeanSpeed("ltkbh_e2_0") + traci.lane.getLastStepMeanSpeed("ltkbh_e2_1"))/2
                    vtb_lg = (traci.lane.getLastStepMeanSpeed("lg_e28_0") + traci.lane.getLastStepMeanSpeed("lg_e29_0"))/2
                    vtb_tht = traci.lane.getLastStepMeanSpeed("tht_e13_0")

                    info = {'id':'ltk_lg','apprid1':'ltklg_bd', 'apprid2':'ltklg_ntd', 'apprid3':'ltklg_lg', 'apprid4':'ltklg_tht', 'vhccome1': len(self.list_vehicle_ltkbd), 'vhccome2': len(self.list_vehicle_ltkntd), 'vhccome3': len(self.list_vehicle_lg), 'vhccome4': len(self.list_vehicle_tht), 'vhcout1': len(self.list_vehiclepass_ltkbd), 'vhcout2': len(self.list_vehiclepass_ltkntd), 'vhcout3': len(self.list_vehiclepass_lg), 'vhcout4': len(self.list_vehiclepass_tht),'vtb1':vtb_ltkbd, 'vtb2': vtb_ltkntd, 'vtb3': vtb_lg, 'vtb4': vtb_tht}      
                    res = requests.get(httphost_putdetails, params = info)                    
                    self.list_vehicle_lg = []
                    self.list_vehicle_tht = []
                    self.list_vehicle_ltkbd = []
                    self.list_vehicle_ltkntd = []
                    self.list_vehiclepass_ltkbd = []
                    self.list_vehiclepass_ltkntd = []
                    self.list_vehiclepass_lg = []
                    self.list_vehiclepass_tht = []
                    putdatadetail = True

            self.countVehicleCome(traci.inductionloop.getIDList())                             

            phase = traci.trafficlights.getPhase("ltk_intersection")          

            if (self.connected == True and self.issetparams == False):
                try:
                    info = {'id':'ltk_lg'}      
                    res = requests.get(httphost_get, params = info) 
                    self.connected = True
                except:
                    self.connected = False 
                    print("connect fail")                    

                if (res.json()['isparams'] == True):    
                    print("set params")
                    self.ltk_green = res.json()['phase1']
                    self.set_phase_ltk = True 
                   
                    self.lgtht_green = res.json()['phase2']  
                    self.set_phase_lgtht = True 
                
                if (self.isfirst == True):
                    global fltk_green, flgtht_green
                    if (phase == 0):
                        self.fltk_green = int(traci.trafficlights.getPhaseDuration("ltk_intersection"))
                    if (phase == 2):  
                        self.flgtht_green = int(traci.trafficlights.getPhaseDuration("ltk_intersection"))

                    if (self.fltk_green != 0 and self.flgtht_green != 0):    
                        info = {'id':'ltk_lg', 'p1': self.fltk_green, 'p2': self.flgtht_green, 'firstparams': False}   
                        res = requests.get(httphost_put, params = info)
                        self.isfirst = False
                        print("put param to server")  
                        print(self.fltk_green) 
                        print(self.flgtht_green)

                if (self.set_phase_ltk == True and phase == 0 and int(self.ltk_green) > 10): 
                    old_ltk_green = traci.trafficlights.getPhaseDuration("ltk_intersection")
                    print(old_ltk_green)
                    if(int(self.ltk_green) != int(old_ltk_green)):
                        traci.trafficlights.setPhaseDuration("ltk_intersection", int(self.ltk_green))
                        self.set_phase_ltk = False
                        print("success ltk: ",int(self.ltk_green))
                        info = {'id':'ltk_lg','bparams': False}   
                        res = requests.get(httphost_put, params = info)
                   
                if (self.set_phase_lgtht == True and phase == 2 and int(self.lgtht_green) > 10): 
                    old_lgtht_green = traci.trafficlights.getPhaseDuration("ltk_intersection")
                    if(int(self.lgtht_green) != int(old_lgtht_green)):
                        traci.trafficlights.setPhaseDuration("ltk_intersection", int(self.lgtht_green)) 
                        self.set_phase_lgtht = False
                        print("success lgtht: ",self.lgtht_green) 
                        info = {'id':'ltk_lg','bparams': False}   
                        res = requests.get(httphost_put, params = info)
            else: 
                # print("normal")                    
                if (self.set_phase_ltk == True and phase == 0 and int(self.ltk_green) > 10): 
                    old_ltk_green = traci.trafficlights.getPhaseDuration("ltk_intersection")
                    print(old_ltk_green)
                    print(int(self.ltk_green))
                    if(int(self.ltk_green) != int(old_ltk_green)):
                        traci.trafficlights.setPhaseDuration("ltk_intersection", int(self.ltk_green))
                        self.set_phase_ltk = False
                        print("success ltk: ",self.ltk_green)
                        # self.isfirst = True
                        # self.issetparams = False
                    else:   
                        self.set_phase_ltk = False  
                   
                if (self.set_phase_lgtht == True and phase == 2 and int(self.lgtht_green) > 10): 
                    old_lgtht_green = traci.trafficlights.getPhaseDuration("ltk_intersection")
                    if(int(self.lgtht_green) != int(old_lgtht_green)):
                        traci.trafficlights.setPhaseDuration("ltk_intersection", int(self.lgtht_green)) 
                        self.set_phase_lgtht = False
                        print("success lgtht: ",self.lgtht_green)       
                        # self.isfirst = True     
                        # self.issetparams = False   
                    else:
                        self.set_phase_lgtht = False    
                
                if (self.set_phase_ltk == False and self.set_phase_lgtht == False):
                    # print("TaiNgo")
                    self.issetparams = False 

            # print("step ",step)        
            step += 1            
        traci.close()
        sys.stdout.flush() 

    def queueVehicleLength_ltkntd(self):
        # return 0
        # print(traci.lane.getLastStepVehicleIDs(":ltk32_junc1_0_0") + traci.lane.getLastStepVehicleIDs(":ltk32_junc1_0_1"))
        # traci.lane.getLength("ltk32_e10_0")
        minpos_ltkntd = traci.lane.getLength("ltk32_e11_0")
        queue_ltkntd = traci.lane.getLastStepVehicleIDs("ltk32_e11_0") + traci.lane.getLastStepVehicleIDs("ltk32_e11_1")
        for vhcid in queue_ltkntd:
            if traci.vehicle.getSpeed(vhcid) <= 1.38:
                if (minpos_ltkntd > traci.vehicle.getLanePosition(vhcid)):
                    minpos_ltkntd = traci.vehicle.getLanePosition(vhcid)
        length_ltkntd = traci.lane.getLength("ltk32_e11_0") - minpos_ltkntd
        
        minpos_ltkntd = traci.lane.getLength(":ltk32_junc1_0_0")
        queue_ltkntd = traci.lane.getLastStepVehicleIDs(":ltk32_junc1_0_0") + traci.lane.getLastStepVehicleIDs(":ltk32_junc1_0_1")
        for vhcid in queue_ltkntd:
            if traci.vehicle.getSpeed(vhcid) <= 1.38:
                if (minpos_ltkntd > traci.vehicle.getLanePosition(vhcid)):
                    minpos_ltkntd = traci.vehicle.getLanePosition(vhcid)
        if (traci.lane.getLength(":ltk32_junc1_0_0") - minpos_ltkntd) > 0:            
            length_ltkntd =length_ltkntd + traci.lane.getLength(":ltk32_junc1_0_0") - minpos_ltkntd

        minpos_ltkntd = traci.lane.getLength("ltk32_e10_0")
        queue_ltkntd = traci.lane.getLastStepVehicleIDs("ltk32_e10_0") + traci.lane.getLastStepVehicleIDs("ltk32_e10_1")        
        for vhcid in queue_ltkntd:
            if traci.vehicle.getSpeed(vhcid) <= 1.38:
                if (minpos_ltkntd > traci.vehicle.getLanePosition(vhcid)):
                    minpos_ltkntd = traci.vehicle.getLanePosition(vhcid)
        if (traci.lane.getLength("ltk32_e10_0") - minpos_ltkntd) > 0:            
            length_ltkntd =length_ltkntd + traci.lane.getLength("ltk32_e10_0") - minpos_ltkntd    

        print("NTD: ",length_ltkntd)  
        print("Waitting time: ", traci.lane.getWaitingTime("ltk32_e11_0") + traci.lane.getWaitingTime("ltk32_e11_1"))  

    def queueVehicleLength_ltkbd(self):        
        minpos_ltkbd = traci.lane.getLength("ltkbh_e22_0")
        queue_ltkbd = traci.lane.getLastStepVehicleIDs("ltkbh_e22_0") + traci.lane.getLastStepVehicleIDs("ltkbh_e22_1")
        for vhcid in queue_ltkbd:
            if traci.vehicle.getSpeed(vhcid) <= 1.38:
                if (minpos_ltkbd > traci.vehicle.getLanePosition(vhcid)):
                    minpos_ltkbd = traci.vehicle.getLanePosition(vhcid)
        length_ltkbd = traci.lane.getLength("ltkbh_e22_0") - minpos_ltkbd
        
        minpos_ltkbd = traci.lane.getLength(":ltkbh_junc1_9_0")
        queue_ltkbd = traci.lane.getLastStepVehicleIDs(":ltkbh_junc1_9_0") + traci.lane.getLastStepVehicleIDs(":ltkbh_junc1_9_1")
        for vhcid in queue_ltkbd:
            if traci.vehicle.getSpeed(vhcid) <= 1.38:
                if (minpos_ltkbd > traci.vehicle.getLanePosition(vhcid)):
                    minpos_ltkbd = traci.vehicle.getLanePosition(vhcid)
        if (traci.lane.getLength(":ltkbh_junc1_9_0") - minpos_ltkbd) > 0:            
            length_ltkbd =length_ltkbd + traci.lane.getLength(":ltkbh_junc1_9_0") - minpos_ltkbd

        minpos_ltkbd = traci.lane.getLength("ltkbh_e21_0")
        queue_ltkbd = traci.lane.getLastStepVehicleIDs("ltkbh_e21_0") + traci.lane.getLastStepVehicleIDs("ltkbh_e21_1")        
        for vhcid in queue_ltkbd:
            if traci.vehicle.getSpeed(vhcid) <= 1.38:
                if (minpos_ltkbd > traci.vehicle.getLanePosition(vhcid)):
                    minpos_ltkbd = traci.vehicle.getLanePosition(vhcid)
        if (traci.lane.getLength("ltkbh_e21_0") - minpos_ltkbd) > 0:            
            length_ltkbd =length_ltkbd + traci.lane.getLength("ltkbh_e21_0") - minpos_ltkbd    

        print("BD: ",length_ltkbd) 

    def queueVehicleLength_lg(self):        
        minpos_lg = traci.lane.getLength("lg_e30_0")
        queue_lg = traci.lane.getLastStepVehicleIDs("lg_e30_0")
        for vhcid in queue_lg:
            if traci.vehicle.getSpeed(vhcid) <= 1.38:
                if (minpos_lg > traci.vehicle.getLanePosition(vhcid)):
                    minpos_lg = traci.vehicle.getLanePosition(vhcid)
        length_lg = traci.lane.getLength("lg_e30_0") - minpos_lg
        
        minpos_lg = traci.lane.getLength(":lg_junc1_5_0")
        queue_lg = traci.lane.getLastStepVehicleIDs(":lg_junc1_5_0")
        for vhcid in queue_lg:
            if traci.vehicle.getSpeed(vhcid) <= 1.38:
                if (minpos_lg > traci.vehicle.getLanePosition(vhcid)):
                    minpos_lg = traci.vehicle.getLanePosition(vhcid)
        if (traci.lane.getLength(":lg_junc1_5_0") - minpos_lg) > 0:            
            length_lg =length_lg + traci.lane.getLength(":lg_junc1_5_0") - minpos_lg

        minpos_lg = traci.lane.getLength("lg_e29_0")
        queue_lg = traci.lane.getLastStepVehicleIDs("lg_e29_0")     
        for vhcid in queue_lg:
            if traci.vehicle.getSpeed(vhcid) <= 1.38:
                if (minpos_lg > traci.vehicle.getLanePosition(vhcid)):
                    minpos_lg = traci.vehicle.getLanePosition(vhcid)
        if (traci.lane.getLength("lg_e29_0") - minpos_lg) > 0:            
            length_lg =length_lg + traci.lane.getLength("lg_e29_0") - minpos_lg    

        print("LG: ",length_lg)     

    def queueVehicleLength_tht(self):        
        minpos_tht = traci.lane.getLength("tht_e14_0")
        queue_tht = traci.lane.getLastStepVehicleIDs("tht_e14_0")
        for vhcid in queue_tht:
            if traci.vehicle.getSpeed(vhcid) <= 1.38:
                if (minpos_tht > traci.vehicle.getLanePosition(vhcid)):
                    minpos_tht = traci.vehicle.getLanePosition(vhcid)
        length_tht = traci.lane.getLength("tht_e14_0") - minpos_tht
        
        minpos_tht = traci.lane.getLength(":tht_junc1_1_0")
        queue_tht = traci.lane.getLastStepVehicleIDs(":tht_junc1_1_0")
        for vhcid in queue_tht:
            if traci.vehicle.getSpeed(vhcid) <= 1.38:
                if (minpos_tht > traci.vehicle.getLanePosition(vhcid)):
                    minpos_tht = traci.vehicle.getLanePosition(vhcid)
        if (traci.lane.getLength(":tht_junc1_1_0") - minpos_tht) > 0:            
            length_tht =length_tht + traci.lane.getLength(":tht_junc1_1_0") - minpos_tht

        minpos_tht = traci.lane.getLength("tht_e13_0")
        queue_tht = traci.lane.getLastStepVehicleIDs("tht_e13_0")     
        for vhcid in queue_tht:
            if traci.vehicle.getSpeed(vhcid) <= 1.38 and traci.vehicle.getLanePosition(vhcid) > 10:
                if (minpos_tht > traci.vehicle.getLanePosition(vhcid)):
                    minpos_tht = traci.vehicle.getLanePosition(vhcid)
        if (traci.lane.getLength("tht_e13_0") - minpos_tht) > 0:            
            length_tht =length_tht + traci.lane.getLength("tht_e13_0") - minpos_tht    

        print("THT: ",length_tht)      

    def countVehicleCome(self, listInductionLoopId):
        global list_vehicle_ltkbd, list_vehicle_ltkntd, list_vehicle_lg, list_vehicle_tht, list_vehiclepass_ltkbd, list_vehiclepass_ltkntd, list_vehiclepass_lg, list_vehiclepass_tht
        nvhc_lg = []       
        nvhc_tht = []
        nvhc_ltkbd = []
        nvhc_ltkntd = []  

        nvhc_pass_lg = []       
        nvhc_pass_tht = []
        nvhc_pass_ltkbd = []
        nvhc_pass_ltkntd = []  

        for inductionLoopId in listInductionLoopId:
            #count vehicle come
            if 'lg_detector' in inductionLoopId:                  
                nvhc_lg = traci.inductionloop.getLastStepVehicleIDs(inductionLoopId)               
                for vehicleId in nvhc_lg:
                    if (self.list_vehicle_lg.count(vehicleId) == 0):
                        self.list_vehicle_lg.append(vehicleId)                       

            if 'tht_detector' in inductionLoopId:             
                nvhc_tht = traci.inductionloop.getLastStepVehicleIDs(inductionLoopId)  
                for vehicleId in nvhc_tht:
                    if (self.list_vehicle_tht.count(vehicleId) == 0):
                        self.list_vehicle_tht.append(vehicleId)

            if 'ltkbd_detector' in inductionLoopId:             
                nvhc_ltkbd = traci.inductionloop.getLastStepVehicleIDs(inductionLoopId) 
                for vehicleId in nvhc_ltkbd:
                    if (self.list_vehicle_ltkbd.count(vehicleId) == 0):
                        self.list_vehicle_ltkbd.append(vehicleId)

            if 'ltkntd_detector' in inductionLoopId:             
                nvhc_ltkntd = traci.inductionloop.getLastStepVehicleIDs(inductionLoopId)     
                for vehicleId in nvhc_ltkntd:
                    if (self.list_vehicle_ltkntd.count(vehicleId) == 0):
                        self.list_vehicle_ltkntd.append(vehicleId)

            # count vehicle pass     
            if 'ltkbd_pass_detector' in inductionLoopId:             
                nvhc_pass_ltkbd = traci.inductionloop.getLastStepVehicleIDs(inductionLoopId)     
                for vehicleId in nvhc_pass_ltkbd:
                    if (self.list_vehiclepass_ltkbd.count(vehicleId) == 0):
                        self.list_vehiclepass_ltkbd.append(vehicleId)
            # print(inductionLoopId)                        
            # print("ltkbd pass: ", len(self.list_vehiclepass_ltkbd))

            if 'ltkntd_pass_detector' in inductionLoopId:             
                nvhc_pass_ltkntd = traci.inductionloop.getLastStepVehicleIDs(inductionLoopId)     
                for vehicleId in nvhc_pass_ltkntd:
                    if (self.list_vehiclepass_ltkntd.count(vehicleId) == 0):
                        self.list_vehiclepass_ltkntd.append(vehicleId)

            if 'lg_pass_detector' in inductionLoopId:             
                nvhc_pass_lg = traci.inductionloop.getLastStepVehicleIDs(inductionLoopId)     
                for vehicleId in nvhc_pass_lg:
                    if (self.list_vehiclepass_lg.count(vehicleId) == 0):
                        self.list_vehiclepass_lg.append(vehicleId)

            if 'tht_pass_detector' in inductionLoopId:             
                nvhc_pass_tht = traci.inductionloop.getLastStepVehicleIDs(inductionLoopId)     
                for vehicleId in nvhc_pass_tht:
                    if (self.list_vehiclepass_tht.count(vehicleId) == 0):
                        self.list_vehiclepass_tht.append(vehicleId)                                    

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
        global turn_left, turn_right, turn_straight, fields, ltk_green, lgtht_green, set_phase_ltk, set_phase_lgtht, issetparams
        
        
        self.set_phase_ltk = True
        self.set_phase_lgtht = True
        
        for entry in entries:
            if (entry[0] == self.fields[0] and self.is_int(entry[1].get())):
                self.red_light = entry[1].get()
            elif (entry[0] == self.fields[1] and self.is_int(entry[1].get())):
                self.ltk_green = entry[1].get()
            elif (entry[0] == self.fields[2] and self.is_int(entry[1].get())):
                self.lgtht_green = entry[1].get()

        self.issetparams = True        
        print("+ red light : ",int(self.red_light))
        print("+ ltk green : ",self.ltk_green)
        print("+ lgtht green : ",self.lgtht_green)
        
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
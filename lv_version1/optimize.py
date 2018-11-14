import os
import sys
import time
import random
import math

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
        
def determinedelay(c,g,x,t):
    d1 = (c*math.pow((1-g/c),2))/(2*(1-min(x,1)*(g/c)))
    d2 = 15*t*((x-1) + math.sqrt(math.pow((x-1),2) + (240*x)/(c*t)))
    #xet 1 nga tu doc lap d=kf*d1+d2 kf =1 
    d = d1 + d2
    print(d1, d2)
    return d

def optimalCycle():   
    
    #calculating green time for phase i according to flow ratio.
    ge = [0, 0]
    q = []
    s =  []
    y = []
    L = 4
    
    for i in range(2):
        q.append([0]*4)
        s.append([0]*4)
        y.append([0]*4)
        max = 100
        print(max)
        for j in range (4):
            #
            s[i][j] = random.randrange(400,500)            
            # 
            q[i][j] = random.randrange(max)
            print(q[i][j])
            #q[i][j] = 100 
            #
            y[i][j] = float(q[i][j])/float(s[i][j])
             
    Cmax = 120
    qt = 0
    Copt = Cmax
   
    yc = [0, 0]
    for i in range(2):        
        for j in range (4):
            if yc[i] < y [i][j]:
                yc[i] = y[i][j]      
      
      
    print("yc:",yc)            
    for i in range(2):                        
        qt = qt + q[i][j]             
          
    Y = 0            
    for i in range(2):
        Y = Y + yc[i]
        qt = qt + q[i][j]   
    
    dmin = 10000    
    
    Cmin = int(round(L/(1-Y))) + 1
    
    print("cmin", Cmin)
    
    for C in range(Cmin, Cmax + 1):
        gt = C - L 
        Dt = 0
        # 2 phase
        for i in range(2):  
            #is the effective green time for phase i.
            ge[i] = gt*yc[i]/Y   
            for j in range(4):
                dij = determinedelay(C,ge[i],0.85,5)
                Dt = Dt + dij*(float(q[i][j])/float(qt))               
        if dmin > Dt:
            dmin = Dt
            Copt = C
            print ("dmin", dmin)  
        else:
            break              
    Ge = Copt - L
    
    print("copt", Copt)
    for  i in range(2):
        ge[i] = Ge * yc[i] / Y
        
    return ge    
           
                
	
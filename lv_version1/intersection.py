import traci

def countVehicleCome(listInductionLoopId):
    print("step")
    nvhc_lg = []
    listvhc_lg = []
    nvhc_tht = []
    nvhc_ltkbd = []
    nvhc_ltkntd = []    
    for inductionLoopId in listInductionLoopId:
        if 'lg_detector' in inductionLoopId:                  
            nvhc_lg = traci.inductionloop.getLastStepVehicleIDs(inductionLoopId)
            # print(traci.inductionloop.getLastStepVehicleIDs(inductionLoopId))
            for vehicleId in nvhc_lg:
                listvhc_lg.append(vehicleId)
        if 'tht_detector' in inductionLoopId:             
            nvhc_tht = traci.inductionloop.getLastStepVehicleIDs(inductionLoopId)  

        if 'ltkbd_detector' in inductionLoopId:             
            nvhc_ltkbd = traci.inductionloop.getLastStepVehicleIDs(inductionLoopId) 

        if 'ltkntd_detector' in inductionLoopId:             
            nvhc_ltkntd = traci.inductionloop.getLastStepVehicleIDs(inductionLoopId)           

    
    print(listvhc_lg)

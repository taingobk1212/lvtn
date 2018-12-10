from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from blog.models import Traffic, Infointer, trafficlightinfo
import json

def gettrafficdata(request):
    # print request.GET.get('id')
    queryset = Traffic.objects.filter(intersection_id=request.GET.get('id'))
    # queryset = Traffic.objects.all()
    for obj in queryset: 
        print obj.intersection_id
        print obj.intersection_name

    queryset2 = trafficlightinfo.objects.filter(intersection_id=request.GET.get('id'))     
    tl_records = []
    for obj2 in queryset2: 
        record = {"apprid": obj2.appr_id, "apprname": obj2.appr_name, "tlgreen": obj2.tlgreen, "tlyellow": obj2.tlyellow, "tlred": obj2.tlred}
        tl_records.append(record)

    data = json.dumps({'id': obj.intersection_id, 'name': obj.intersection_name, 'isparams': str(obj.is_params), 'trafficlight': tl_records}, indent=4) 
    temp = eval(data)    
    # return JsonResponse({'name':obj.intersection_name,'id':obj.intersection_id, 'phase1':obj.phase_one, 'phase2':obj.phase_two,'apprname1': obj.appr1_name,'apprname2': obj.appr2_name ,'isparams': obj.is_params})
    return JsonResponse(temp)

def getintersectiondata(request):
    # print request.GET.get('id')
    queryset = Infointer.objects.filter(intersection_id=request.GET.get('id'))
    # queryset = Traffic.objects.all()
    jsstring = "{"
    count = 0
    for obj in queryset: 
        if (count > 0):
            jsstring = jsstring + ","
        count += 1        
        jsstring = jsstring + "'" + "apprname" + str(count) + "'" + ":" + "'" + obj.appr_name + "'" +","
        jsstring = jsstring + "'" + "vtb" + str(count) + "'" + ":" + "'" + str(obj.vtb) + "'" + ","
        jsstring = jsstring + "'" + "vhccome" + str(count) + "'" + ":" + "'" + str(obj.vhc_come) + "'" + ","
        jsstring = jsstring + "'" + "vhcout" + str(count) + "'" + ":" + "'" + str(obj.vhc_out) + "'" + ","
        jsstring = jsstring + "'" + "queuelength" + str(count) + "'" + ":" + "'" + str(obj.vhc_queue_length) + "'" + ","
        jsstring = jsstring + "'" + "waittime" + str(count) + "'" + ":" + "'" + str(obj.wait_avrg) + "'"
        
    jsstring = jsstring + ",'" + "count" + "'" + ":"+ str(count) +"}"
    if (count == 0):       
       jsstring = "{'count': 0}"
    # print (jsstring)  
    # print(count)  
    jstemp = eval(jsstring)
    # return JsonResponse({'id':obj.intersection_id})        
    return JsonResponse(jstemp)
      

def puttrafficdata(request):        
    queryset = Traffic.objects.filter(intersection_id=request.GET.get('id'))
    for obj in queryset:         
        # request from sumo
        if (request.GET.get('bparams') == 'False'):
            print("sumo ok")
            obj.is_params = False            
            obj.save()
        elif (request.GET.get('tlauto') == 'True'):
            print("auto ok")
            obj.is_auto = True  
            obj.save()   
        else:   
            if (request.GET.get('firstparams') == 'False'):
                obj.is_params = False
            else:
                obj.is_params = True   
            obj.save()
        
    # return HttpResponse('{\"id\":' + obj.intersection_id + ',\"phase1\":'+ obj.phase_one + ',\"phase2\":'+obj.phase_two+'}')   
    return JsonResponse({'name':obj.intersection_name,'id':obj.intersection_id, 'phase1':obj.phase_one, 'phase2':obj.phase_two, 'isparams': obj.is_params})   

def putdatadetails(request):    
    queryset = Infointer.objects.filter(intersection_id=request.GET.get('id'))
    for obj in queryset: 
        if (obj.appr_id == request.GET.get('apprid1')):           
           obj.vhc_come = request.GET.get('vhccome1')
           obj.vhc_out = request.GET.get('vhcout1')
           obj.vtb = request.GET.get('vtb1')
           obj.vhc_queue_length = request.GET.get('queue_length1')
           obj.wait_avrg = request.GET.get('waittime1')
           obj.save()  
        if (obj.appr_id == request.GET.get('apprid2')):
           obj.vhc_come = request.GET.get('vhccome2')
           obj.vhc_out = request.GET.get('vhcout2')   
           obj.vtb = request.GET.get('vtb2')  
           obj.vhc_queue_length = request.GET.get('queue_length2')
           obj.wait_avrg = request.GET.get('waittime2')
           obj.save()      
        if (obj.appr_id == request.GET.get('apprid3')):
           obj.vhc_come = request.GET.get('vhccome3')
           obj.vhc_out = request.GET.get('vhcout3')   
           obj.vtb = request.GET.get('vtb3')
           obj.vhc_queue_length = request.GET.get('queue_length3')
           obj.wait_avrg = request.GET.get('waittime3')
           obj.save()         
        if (obj.appr_id == request.GET.get('apprid4')):
           obj.vhc_come = request.GET.get('vhccome4')  
           obj.vhc_out = request.GET.get('vhcout4')   
           obj.vtb = request.GET.get('vtb4')
           obj.vhc_queue_length = request.GET.get('queue_length4')
           obj.wait_avrg = request.GET.get('waittime4')
           obj.save()  

    return JsonResponse({'result':'normal'})

def puttrafficlightdata(request):            
    queryset = trafficlightinfo.objects.filter(intersection_id=request.GET.get('id'), appr_id=request.GET.get('apprid'))
    for obj in queryset:   
        obj.tlgreen = request.GET.get('tlgreen')  
        obj.tlyellow = request.GET.get('tlyellow')  
        obj.tlred = request.GET.get('tlred')  
        obj.save()  

    queryset1 = Traffic.objects.filter(intersection_id=request.GET.get('id'))    
    for obj1 in queryset1: 
        if (request.GET.get('issetparams') == 'True'):            
            obj1.is_params = True
        else:
            obj1.is_params = False     
        obj1.save()  

    return JsonResponse({'result':'normal'})   
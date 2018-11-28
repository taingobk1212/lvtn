from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from blog.models import Traffic, Infointer
import json

def gettrafficdata(request):
    # print request.GET.get('id')
    queryset = Traffic.objects.filter(intersection_id=request.GET.get('id'))
    # queryset = Traffic.objects.all()
    for obj in queryset: 
        print obj.intersection_id
        print obj.intersection_name
        print obj.phase_one
        print obj.phase_two     
    # return HttpResponse('{\"id\":' + obj.intersection_id + ',\"phase1\":'+ obj.phase_one + ',\"phase2\":'+obj.phase_two+'}')   
    return JsonResponse({'name':obj.intersection_name,'id':obj.intersection_id, 'phase1':obj.phase_one, 'phase2':obj.phase_two,'apprname1': obj.appr1_name,'apprname2': obj.appr2_name ,'isparams': obj.is_params})

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
    print (jsstring)  
    print(count)  
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
            obj.phase_one = request.GET.get('p1')
            obj.phase_two = request.GET.get('p2')
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
           obj.vhc_queue_length = request.GET.get('queue_elength1')
           obj.wait_avrg = request.GET.get('waittime1')
           obj.save()  
        if (obj.appr_id == request.GET.get('apprid2')):
           obj.vhc_come = request.GET.get('vhccome2')
           obj.vhc_out = request.GET.get('vhcout2')   
           obj.vtb = request.GET.get('vtb2')  
           obj.vhc_queue_length = request.GET.get('queue_elength2')
           obj.wait_avrg = request.GET.get('waittime2')
           obj.save()      
        if (obj.appr_id == request.GET.get('apprid3')):
           obj.vhc_come = request.GET.get('vhccome3')
           obj.vhc_out = request.GET.get('vhcout3')   
           obj.vtb = request.GET.get('vtb3')
           obj.vhc_queue_length = request.GET.get('queue_elength3')
           obj.wait_avrg = request.GET.get('waittime3')
           obj.save()         
        if (obj.appr_id == request.GET.get('apprid4')):
           obj.vhc_come = request.GET.get('vhccome4')  
           obj.vhc_out = request.GET.get('vhcout4')   
           obj.vtb = request.GET.get('vtb4')
           obj.vhc_queue_length = request.GET.get('queue_elength4')
           obj.wait_avrg = request.GET.get('waittime4')
           obj.save()  

         
    return JsonResponse({'result':'normal'})
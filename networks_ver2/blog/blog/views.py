from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from blog.models import Traffic

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
    return JsonResponse({'name':obj.intersection_name,'id':obj.intersection_id, 'phase1':obj.phase_one, 'phase2':obj.phase_two, 'isparams': obj.is_params})    

def puttrafficdata(request):        
    queryset = Traffic.objects.filter(intersection_id=request.GET.get('id'))
    for obj in queryset:         
        # request from sumo
        if (request.GET.get('bparams') == 'False'):
            print("sumo ok")
            obj.is_params = False            
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
    return JsonResponse({'name':obj.intersection_name,'id':obj.intersection_id, 'phase1':obj.phase_one, 'phase2':obj.phase_twom, 'isparams': obj.is_params})   
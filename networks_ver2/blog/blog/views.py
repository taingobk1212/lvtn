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
        print obj.phase_one
        print obj.phase_two     
    # return HttpResponse('{\"id\":' + obj.intersection_id + ',\"phase1\":'+ obj.phase_one + ',\"phase2\":'+obj.phase_two+'}')   
    return JsonResponse({'id':obj.intersection_id, 'phase1':obj.phase_one, 'phase2':obj.phase_two})   

def puttrafficdata(request):
    print("test")
    print(request.GET.get('p2'))
    queryset = Traffic.objects.filter(intersection_id=request.GET.get('id'))
    for obj in queryset: 
       obj.phase_one = request.GET.get('p1')
       obj.phase_two = request.GET.get('p2')
       obj.save()
    # return HttpResponse('{\"id\":' + obj.intersection_id + ',\"phase1\":'+ obj.phase_one + ',\"phase2\":'+obj.phase_two+'}')   
    return JsonResponse({'id':obj.intersection_id, 'phase1':obj.phase_one, 'phase2':obj.phase_two})   
from django.shortcuts import render
import json
from django.http import HttpResponse
from django.template import RequestContext
from django.contrib.auth.models import User
from django.http import HttpResponse

# Create your views here.
def catalogo(request):
    response = {"status": False, "errors": []}
    if request.method == 'POST':
        var = request.POST['uno']

        response["status"] = True

        response["student"] = {}

        response["user_info"] = {}
    
    return HttpResponse(json.dumps(response))

def descarga(request):
    response = {"status": False, "errors": []}
    if request.method == 'POST':
        var = request.POST['uno']

        response["status"] = True

        response["student"] = {}

        response["user_info"] = {}
    
    return HttpResponse(json.dumps(response))

def ndvi(request):
    response = {"status": False, "errors": []}
    if request.method == 'POST':
        var = request.POST['uno']

        response["status"] = True

        response["student"] = {}

        response["user_info"] = {}
    
    return HttpResponse(json.dumps(response))

def borrar(request):
    response = {"status": False, "errors": []}
    if request.method == 'POST':
        var = request.POST['uno']

        response["status"] = True

        response["student"] = {}

        response["user_info"] = {}
    
    return HttpResponse(json.dumps(response))

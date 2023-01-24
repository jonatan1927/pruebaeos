from django.shortcuts import render
import json
from django.http import HttpResponse
from django.template import RequestContext
from django.contrib.auth.models import User
from django.http import HttpResponse
from recursos.prueba_pesca import JVVEarthExplorer
import os
from descargaimgs.settings import BASE_DIR

# Create your views here.
def catalogo(request):
    response = {}
    if request.method == 'POST':
        received_json_data=json.loads(request.body)
        datos = JVVEarthExplorer.listarscenes(received_json_data)

        response["escenas_encontradas"] = len(datos)
        response["escenas"] = datos
    
    return HttpResponse(json.dumps(response))

def descarga(request):
    response = {}
    if request.method == 'POST':
        received_json_data=json.loads(request.body)
        folder = (received_json_data["output_dir"]).split("/")
        urltemp = (request.build_absolute_uri()).replace("descarga", folder[1])
        url = os.path.join(urltemp,received_json_data["escena"])
        if received_json_data["accion"] == "descarga" :
            datosUno = JVVEarthExplorer.descargar(received_json_data["escena"], received_json_data["output_dir"])
            response["escena"] = received_json_data["escena"]
            response["url"] = url

        else :
            datosDos = JVVEarthExplorer.listaimg(received_json_data["escena"], received_json_data["output_dir"])
            if len(datosDos) == 0:
                response["escena"] = received_json_data["escena"]
                response["mensaje"] =  "escena no encontrada"  
            else:
                response["escena"] = received_json_data["escena"]
                response["url"] = url       
                response["archivos"] = datosDos      
    return HttpResponse(json.dumps(response))

def ndvi(request):
    response = {}

    if request.method == 'POST':
        received_json_data=json.loads(request.body)
        datos = JVVEarthExplorer.ndvi(received_json_data)
        response["ndvi"] = datos
    
    return HttpResponse(json.dumps(response))

def borrar(request):
    response = {}

    if request.method == 'POST':

        received_json_data=json.loads(request.body)
        datos = JVVEarthExplorer.delete(received_json_data)
        response["mensaje"] = datos
    
    return HttpResponse(json.dumps(response))

# -*- coding: utf-8 -*-

import json
from landsatxplore.api import API
from recursos.earthexplorerlocal import EarthExplorerLocal
import tarfile
# import OS module
import os
import shutil

import requests
import sys
import time

import rasterio
import rasterio.features
import rasterio.warp

class JVVEarthExplorer(object):

    def descargar(scene, folder):

        # try:
        username = "jvelasquezvdgh"
        password = "Usgsjvv2023#"

        ee = EarthExplorerLocal(username, password)
        ee.download(scene, output_dir=folder)
        ee.logout()

        test_file_name = folder+"/"+scene+".tar"
        # open file
        file = tarfile.open(test_file_name)
        # extracting file
        file.extractall(folder+"/"+scene)
        file.close()

        os.remove(folder+"/"+scene+".tar")

    def listaimg(scene, folder):
        # This is my path
        path = folder+"/"+scene
        print(path)
        # to store files in a list
        list = []
        # dirs=directories
        for (root, dirs, file) in os.walk(path):
            for f in file:
                if 'T1_B' in f:
                # print(f)
                    tempUno = f.split("_")
                    tempDos = (tempUno[len(tempUno) - 1]).replace(".TIF", "").replace("B", "Banda")
                    list.append({tempDos : f})
        return list

    def delete(scene):
        nombre = scene['escena']
        # Deleting an non-empty folder
        dir_path = "./temporal/"+nombre
        shutil.rmtree(dir_path, ignore_errors=True)
        print("Deleted '%s' directory successfully" % dir_path)
        return "ok"

    def listarscenes(parameters):

        def sendRequest(url, data, apiKey=None):
            json_data = json.dumps(data)

            if apiKey == None:
                response = requests.post(url, json_data)
            else:
                headers = {'X-Auth-Token': apiKey}
                response = requests.post(url, json_data, headers=headers)

            try:
                httpStatusCode = response.status_code
                if response == None:
                    print("No output from service")
                    sys.exit()
                output = json.loads(response.text)
                if output['errorCode'] != None:
                    print(output['errorCode'], "- ", output['errorMessage'])
                if httpStatusCode == 404:
                    print("404 Not Found")
                    sys.exit()
                elif httpStatusCode == 401:
                    print("401 Unauthorized")
                    sys.exit()
                elif httpStatusCode == 400:
                    print("Error Code", httpStatusCode)
                    sys.exit()
            except Exception as e:
                response.close()
                print(e)
                sys.exit()
            response.close()

            return output

        # print("papo "+ parameters["lat"])

        username = "jvelasquezvdgh"
        password = "Usgsjvv2023#"  

        print("\nRunning Scripts...\n")
        
        serviceUrl = "https://m2m.cr.usgs.gov/api/api/json/experimental/"
        
        # Login
        payload = {'username' : username, 'password' : password}
        
        print("\nLogin...\n")
        
        response = sendRequest(serviceUrl + "login", payload)
        
        if response['errorCode'] == None:
            apiKey = response['data']
        else:
            sys.exit()
        
        print("API Key: " + apiKey + "\n") 
      
        datasetName = parameters["dataset"]
        
        spatialFilter = {
                        "geoJson": {
                            "type": "Point",
                            "coordinates": [float(parameters["lon"]), float(parameters["lat"])]
                        },
                        "filterType": "geojson"
                    }
                        
        temporalFilter = {'start' : parameters["fecha_inicio"], 'end' : parameters["fecha_fin"]}

        CloudCoverFilter = {'max' : parameters["nubosidad_max"] }
        
        searchCreatePayload = {'datasetName' : datasetName,
                                'spatialFilter' : spatialFilter,
                                'temporalFilter' : temporalFilter,
                                'CloudCoverFilter' :  CloudCoverFilter}                 
        
        print("Creating a search request...\n")
        response = sendRequest(serviceUrl + "scene-search", searchCreatePayload, apiKey)
        if response['errorCode'] == None:
            searchId = response['data']['results']
        else:
            sys.exit()
        # print(f"Search {searchId} created\n")

        salida = [] 
        for result in searchId:
            # The details of scene-search-results response can be found here: https://m2m.cr.usgs.gov/api/docs/reference/#scene-search-results
            # print (result['entityId']) 
            # print (result['displayId']) 
            date = (result['temporalCoverage']['startDate']).split(" ")
            # print (date[0]) 
            salida.append({"fecha": date[0], "identificador": result['displayId']})
            # TODO: get you want with the product
                    
        # Logout so the API Key cannot be used anymore
        endpoint = "logout" 
        sendRequest(serviceUrl + endpoint, {}, apiKey) 
        return salida      

    def ndvi(parameters):
        img = parameters["escena"] 
        lon = parameters["lon"]
        lat = parameters["lat"]

        dat = rasterio.open("./temporal/" + img + "/" + img + "_B4.TIF")
        print(dat)
        # read all the data from the first band
        z = dat.read()[0]

        print(z)

        # check the crs of the data
        # dat.crs
        # >>> CRS.from_epsg(4326)

        # check the bounding-box of the data
        # dat.bounds
        # >>> Out[49]: BoundingBox(left=-120.0, bottom=45.0, right=-117.0, top=48.0)

        # since the raster is in regular lon/lat grid (4326) we can use 
        # `dat.index()` to identify the index of a given lon/lat pair
        # (e.g. it expects coordinates in the native crs of the data)

        # idx = dat.index(float(lon), float(lat), precision=1E-6)    
        # return dat.xy(*idx), z[idx]



# https://gis.stackexchange.com/questions/428728/get-lanlon-and-values-from-geotiff-using-python
# https://developers.planet.com/docs/planetschool/calculate-an-ndvi-in-python/
# https://github.com/yannforget/landsatxplore
# https://pypi.org/project/landsat-util/
# https://github.com/Fergui/m2m-api
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
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio import plot
import matplotlib.pyplot as plt
import numpy as np



import os
from subprocess import Popen,PIPE

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
                if 'T1_B' in f or 'T2_B' in f :
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

        CloudCoverFilter = {'max' : parameters["nubosidad_max"], 'min': 0, 'includeUnknown': True}
        
        # searchCreatePayload = {'datasetName' : datasetName,
        #                         'spatialFilter' : spatialFilter,
        #                         'temporalFilter' : temporalFilter,
        #                         'CloudCoverFilter' :  CloudCoverFilter}  

        searchCreatePayload = {'datasetName' : datasetName,
                                'sceneFilter' :{
                                    "spatialFilter":spatialFilter,
                                    "cloudCoverFilter":CloudCoverFilter,
                                    "acquisitionFilter":temporalFilter
                                }
                            }                 
        
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

        if os.path.exists("./temporal/ndviImage3.tiff"):
            os.remove("./temporal/ndviImage3.tiff")

        if os.path.exists("./temporal/ndviImagewgs84.tiff"):
            os.remove("./temporal/ndviImagewgs84.tiff")
        
        escena = parameters["escena"]
        lat =  float(parameters["lat"])
        lon = float(parameters["lon"])

        tempUno = escena.split("_")
        print((tempUno[0])[-2:])
        tempDos = (tempUno[0])[-2:]

        imagePath = './temporal/'+escena+'/'
        if tempDos == '05' or tempDos == '07' :
            banda3 = rasterio.open(imagePath+ escena + '_B3.TIF')
            banda4 = rasterio.open(imagePath+ escena + '_B4.TIF')
        else :
            banda3 = rasterio.open(imagePath+ escena + '_B4.TIF')
            banda4 = rasterio.open(imagePath+ escena + '_B5.TIF')

        red = banda3.read(1).astype('float64')
        nir = banda4.read(1).astype('float64')

        ndvi = np.where(
            (nir+red)== 0.,
            0,
            (nir-red)/(nir+red)
        )

        ndviImage = rasterio.open('./temporal/ndviImage3.tiff', 'w', driver='Gtiff',
                        width=banda3.width, height=banda3.height,
                        count=1,
                        crs=banda3.crs,
                        transform=banda3.transform,
                        dtype='float64'
                        )
        ndviImage.write(ndvi,1)
        ndviImage.close()

        #open source raster
        srcRst = rasterio.open('./temporal/ndviImage3.tiff')
        print("source raster crs:")
        print(ndviImage.crs)

        dstCrs = {'init': 'EPSG:4326'}
        print("destination raster crs:")
        print(dstCrs)

        #calculate transform array and shape of reprojected raster
        transform, width, height = calculate_default_transform(
                srcRst.crs, dstCrs, srcRst.width, srcRst.height, *srcRst.bounds)
        print("transform array of source raster")
        print(srcRst.transform)

        print("transform array of destination raster")
        print(transform)

        #working of the meta for the destination raster
        kwargs = srcRst.meta.copy()
        kwargs.update({
                'crs': dstCrs,
                'transform': transform,
                'width': width,
                'height': height
            })
        #open destination raster
        dstRst = rasterio.open('./temporal/ndviImagewgs84.tiff', 'w', **kwargs)
        #reproject and save raster band data
        for i in range(1, srcRst.count + 1):
            reproject(
                source=rasterio.band(srcRst, i),
                destination=rasterio.band(dstRst, i),
                #src_transform=srcRst.transform,
                src_crs=srcRst.crs,
                #dst_transform=transform,
                dst_crs=dstCrs,
                resampling=Resampling.nearest)
        #close destination raster
        dstRst.close()

        x1,y1 = lon, lat

        ndviRaster = rasterio.open('./temporal/ndviImagewgs84.tiff')
        row, col = ndviRaster.index(x1,y1)
        jvv = ndviRaster.read(1)[row,col]

        return jvv




# https://gis.stackexchange.com/questions/428728/get-lanlon-and-values-from-geotiff-using-python
# https://developers.planet.com/docs/planetschool/calculate-an-ndvi-in-python/
# https://github.com/yannforget/landsatxplore
# https://pypi.org/project/landsat-util/
# https://github.com/Fergui/m2m-api
# https://hatarilabs.com/ih-en/extract-point-value-from-a-raster-file-with-python-geopandas-and-rasterio-tutorial
# https://zectre.github.io/geospatialpython/2021/08/08/NDVI-With-Rasterio.html
# https://developers.planet.com/docs/planetschool/calculate-an-ndvi-in-python/
# https://readthedocs.org/projects/rasterio/downloads/pdf/stable/
# https://rasterio.readthedocs.io/en/latest/topics/index.html
# https://rasterio.readthedocs.io/en/latest/topics/georeferencing.html
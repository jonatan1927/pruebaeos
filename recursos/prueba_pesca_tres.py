# =============================================================================
#  USGS/EROS Inventory Service Example
#  Python - JSON API
#
#  Script Last Modified: 1/24/2022
#  Note: This example does not include any error handling!
#        Any request can throw an error, which can be found in the errorCode proprty of
#        the response (errorCode, errorMessage, and data properies are included in all responses).
#        These types of checks could be done by writing a wrapper similiar to the sendRequest function below
#  Usage: python scene_search.py -u username -p password
# =============================================================================

import json
import requests
import sys
import time
import argparse

# Send http request


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


if __name__ == '__main__':
    # NOTE :: Passing credentials over a command line arguement is not considered secure
    #        and is used only for the purpose of being example - credential parameters
    #        should be gathered in a more secure way for production usage
    # Define the command line arguements

    # User input
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-u', '--username', required=True, help='Username')
    # parser.add_argument('-p', '--password', required=True, help='Password')

    # args = parser.parse_args()

    # username = args.username
    # password = args.password

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
    
    # Scene-search-create - it'll return a search ID in the data field   
    # searchCreatePayload = {
    #     "autoExecute": False, # If set to true, there is no need to call scene-search-execute
    #     "searchLabel": "Test Search",
    #     "metadataConfig": None,
    #     "resultsPerPage": 100,
    #     "compareListName": "test-compare",
    #     "excludeListName": "test-exclude",
    #     "datasetName": "landsat_ot_c2_l1",
    #     "maxResults" : "1"
    # }   

    datasetName = "landsat_ot_c2_l1"
    
    spatialFilter = {
                    "geoJson": {
                        "type": "Point",
                        "coordinates": [-78.6298, 1.8035]
                    },
                    "filterType": "geojson"
                }
                     
    temporalFilter = {'start' : '2013-05-03', 'end' : '2013-05-10'}

    CloudCoverFilter = {'max' : 10 }
    
    searchCreatePayload = {'datasetName' : datasetName,
                               'spatialFilter' : spatialFilter,
                               'temporalFilter' : temporalFilter,
                               'CloudCoverFilter' : CloudCoverFilter,
                               'maxResults' : "1"}                 
    
    print("Creating a search request...\n")
    response = sendRequest(serviceUrl + "scene-search", searchCreatePayload, apiKey)
    if response['errorCode'] == None:
        searchId = response['data']['results']
    else:
        sys.exit()
    # print(f"Search {searchId} created\n")

        
    for result in searchId:
        # The details of scene-search-results response can be found here: https://m2m.cr.usgs.gov/api/docs/reference/#scene-search-results
        print (result['entityId']) 
        # TODO: get you want with the product
                
    # Logout so the API Key cannot be used anymore
    endpoint = "logout" 
    if sendRequest(serviceUrl + endpoint, {}, apiKey) == None:        
        print("Logged Out\n")
    else:
        print("Logout Failed\n")

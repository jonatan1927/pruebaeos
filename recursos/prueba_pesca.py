# -*- coding: utf-8 -*-

import json
from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer
import tarfile
# import OS module
import os
import shutil


# funcion del main
if __name__ == '__main__':
    # try:
    print("\nHola a todos\n")
    username = "jvelasquezvdgh"
    password = "Usgsjvv2023#"

    # ee = EarthExplorer(username, password)
    # ee.download('LE07_L1TP_010059_20000117_20200918_02_T1', output_dir='./data')
    # ee.logout()


    # test_file_name = "./data/LT05_L1GS_010059_20110531_20200822_02_T2.tar"
    # # open file
    # file = tarfile.open(test_file_name)
    # # extracting file
    # file.extractall("./data/LT05_L1GS_010059_20110531_20200822_02_T2")
    # file.close()

    os.remove("./data/LT05_L1GS_010059_20110531_20200822_02_T.tar")


    # # This is my path
    # path = "./data/LT05_L1GS_010059_20110531_20200822_02_T2"
    # # to store files in a list
    # list = []
    # # dirs=directories
    # for (root, dirs, file) in os.walk(path):
    #     for f in file:
    #         # if '.txt' in f:
    #         print(f)



    # # Deleting an non-empty folder
    # dir_path = "./data/LT05_L1GS_010059_20110531_20200822_02_T2"
    # shutil.rmtree(dir_path, ignore_errors=True)
    # print("Deleted '%s' directory successfully" % dir_path)



# jvelasquezvdgh
# Usgsjvv2023#

# https://gis.stackexchange.com/questions/428728/get-lanlon-and-values-from-geotiff-using-python
# https://developers.planet.com/docs/planetschool/calculate-an-ndvi-in-python/
# https://github.com/yannforget/landsatxplore
# https://pypi.org/project/landsat-util/
# https://github.com/Fergui/m2m-api
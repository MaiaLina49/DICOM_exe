# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 17:26:46 2021

@author: maial
"""
import tarfile
import wget
import pydicom
import gdcm
import os
import statistics
import pandas as pd


def dataDownload():
    print("Downloading file......")
    dfile=wget.download("https://s3.amazonaws.com/viz_data/DM_TH.tgz")
    print("Extracting files......")
    tf=tarfile.open("DM_TH.tgz")
    tf.extractall(r'files_extract')
    print("Done extracting files.")
 
def clean_text(string):
    forbidden_symbols = ["*", ".", ",", "\"", "\\", "/", "|", "[", "]", ":", ";", " "]
    for symbol in forbidden_symbols:
        string = string.replace(symbol, "_")
    return string.lower()
 
def arrangeFiles():
    print('Arranging files........')
    source='files_extract'
    destination='data'
    for root, dirs, files in os.walk(source):
        for file in files:
            if '.dcm' in file:
                ds = pydicom.read_file(os.path.join(root, file), force=True)
                patientID = clean_text(ds.PatientName.__str__())
                studyID = clean_text(ds.get("StudyInstanceUID", "NA"))
                seriesID = clean_text(ds.get("SeriesInstanceUID", "NA"))
                try:
                    ds.decompress() #some of the images are compresed //// gdcm
                except:
                    pass
                if not os.path.exists(os.path.join(destination, patientID)):
                    os.makedirs(os.path.join(destination, patientID)) 
                if not os.path.exists(os.path.join(destination, patientID, studyID)):
                    os.makedirs(os.path.join(destination, patientID, studyID))
                if not os.path.exists(os.path.join(destination, patientID, studyID, seriesID)):
                    os.makedirs(os.path.join(destination, patientID , studyID, seriesID))
                   
                ds.save_as(os.path.join(destination, patientID, studyID, seriesID, file))
                print(f'file {file} was stored.')
    print('Done arranging files.')
                        
                
def patientList():
    patients=pd.DataFrame(columns = ['Name','Age','Sex','Date' ])
    for root, dirs, files in os.walk('data'):
        if len(files)>0:
            ds = pydicom.read_file(os.path.join(root, files[0]), force=True)
            # for patient name I could use root.split('\\')[1] , but in real life the root folder suposed to be patient Id 
            # I added study time, becuse each patient potentioally has more than one study in diffrent dates  
            dict1={'Name':ds.PatientName.__str__(),'Age':int(ds.PatientAge.replace('Y','')), 'Sex':ds.get("PatientSex"), 'Date':ds.get("StudyDate")  }
            patients=patients.append(dict1, ignore_index=True)
    print("Patient list:\n",patients.drop_duplicates())
        
               

def CT_Duration_option1():
    exposure=[]
    for root, dirs, files in os.walk('data'):
        if len(files)>0:
            ds = pydicom.read_file(os.path.join(root, files[0]), force=True)
            exposure.append(ds.get("ExposureTime"))
    print("CT scan AVG. duration (option 1): {:.2f} seconds".format(statistics.mean(exposure)/1000))    # I'm not sure this is the answer for whole CT scan , I think the answer should be a few minutes 

def CT_Duration_option2():
    durations=[]
    for root, dirs, files in os.walk('data'):
        if len(files)>0:
            ds_1 = pydicom.read_file(os.path.join(root, files[0]), force=True)
            duration=float(ds_1[0x0008,0x0031].value)-float(ds_1[0x0008,0x0030].value)
            durations.append(duration)
    print("CT scan AVG. duration (option 2): {:.2f} minutes".format(statistics.mean(durations))) # I think CT scan won't take more than 30 minutes 


def numOfHospials():
    hospitals=set()
    for root, dirs, files in os.walk('data'):
        if len(files)>0:
            ds = pydicom.read_file(os.path.join(root, files[0]), force=True)
            hospitals.add(ds.get("InstitutionName"))
    print(f"The data comes from {len(hospitals)} diffrent hospitals")  
           
  
      

if __name__=="__main__":
    #dataDownload()
    #arrangeFiles()
    patientList()
    CT_Duration_option1()
    CT_Duration_option2()
    numOfHospials()

    
    
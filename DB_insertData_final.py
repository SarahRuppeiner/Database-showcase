# -*- coding: utf-8 -*-
"""
Created on Thu May  2 16:59:50 2024

@author: srupp
"""

import sqlite3
import pandas as pd

#Connect to the SQLite database
conn = sqlite3.connect('DB_project.sqlite')
cur = conn.cursor()

#Function to read data from files and insert into the database
def fileReader(fname):
    try:
        #Read data from CSV files using pandas
        print(fname)
        if fname.endswith("PLA.csv"):
            colums = ["ExperimentID", "name", "area", "Sphase_filter", "area_filter", "ImageNumb", "Z", "c2_median", "well_ID", "c4_FociCount"]
            dfsmall = pd.read_csv(fname, usecols=colums)
        if fname.endswith("IF.csv"):
            colums = ["ExperimentID", "name", "area", "Sphase_filter", "area_filter", "ImageNumb", "Z", "c2_median", "well_ID"]
            dfsmall = pd.read_csv(fname, usecols=colums)
    except:
        print("not a valid filepath")
    
    #fill sphase_filter table
    sphase_filters = dfsmall.loc[:,"Sphase_filter"].unique()
    for sphase_filter in sphase_filters: 
        cur.execute("INSERT OR IGNORE INTO filter_sphase (id)VALUES (?)", ( sphase_filter, ))
    
    #fill area_filter table
    area_filters = dfsmall.loc[:,"area_filter"].unique()
    for area_filter in area_filters:
        cur.execute("INSERT OR IGNORE INTO filter_area (id)VALUES (?)", ( area_filter, ))
    
    #fill Experiment_type and Experiment
    experimentID = dfsmall.loc[:,"ExperimentID"].unique() #this is ID of the experiment table eg SR001_IF
    print(experimentID)
    experimentIDStr = str(experimentID) 
    experimentIDStr = experimentIDStr.strip("[]\'")
    experimentNR = experimentIDStr.split("_")[0] 
    experimentNR = experimentNR.strip("[]\'") #this is the number eg SR001
    experimenType = experimentIDStr.strip("[]\'").split("_")[1] #this is the type eg IF - with a foreign constraint
    cur.execute("INSERT OR IGNORE INTO Experiment_type (id)VALUES (?)", ( experimenType, ))
    #only works if there is one experiment per file!
    cur.execute("INSERT OR IGNORE INTO experiment (id, experiment_nr, etype_id)VALUES (?,?, ?)", ( experimentIDStr, experimentNR, experimenType)) #no ignore, drop table if you want to overwrite an experiment
    
    #fill treatment_type and treatment
    treatments = dfsmall.loc[:,"name"].unique()
    ltreat = []
    ltreat_type = []
    for treatment in treatments:
        treatment_ID = experimentIDStr + "_" + str(treatment)
        onetreat = (treatment_ID, experimentIDStr, treatment)
        ltreat.append(onetreat)
        temp_treat_type = treatment.split("_")
        main = temp_treat_type[0]
        sub = temp_treat_type[1]
        onetreat_type = (treatment, main, sub)
        ltreat_type.append(onetreat_type)
    cur.executemany("INSERT OR IGNORE INTO treatment (id, experiment_id, ttype_id)VALUES (?,?, ?)", (ltreat))
    cur.executemany("INSERT OR IGNORE INTO treatment_type (id, main, sub)VALUES (?, ?, ?)", ( ltreat_type))
    
    #Fill Cell table based on experiment type
    ldataCell = []
    if experimenType == "IF":
        ldataCell = IF_data(dfsmall, treatment_ID)
    elif experimenType == "PLA":
        ldataCell = PLA_data(dfsmall, treatment_ID)
    cur.executemany("INSERT INTO cell (treatment_id, image_nr, z_plane, well_Nr, filter_sphase, filter_area, area, c2_median, foci_count) VALUES (?,?,?,?,?,?,?,?,?)", (ldataCell))
    conn.commit()

#Function to process data for IF experiments
def IF_data(dfsmall, treatment_ID):
    counter = 0
    lwholeCell = []
    for index,row in dfsmall.iterrows():
        area = row["area"]
        sphase_filters = row["Sphase_filter"]
        area_filters = row["area_filter"]
        imageNr = row["ImageNumb"]
        z_plane = row["Z"]
        c2_median = row["c2_median"]
        focicount = None
        well_Nr = row["well_ID"]
        tlineCell = (treatment_ID, imageNr, z_plane, well_Nr, sphase_filters, area_filters, area, c2_median, focicount)
        lwholeCell.append(tlineCell)
        counter = counter+1
        if counter % 10000 == 0 : 
            print("So many lines are done:", counter)
    return(lwholeCell)

#Function to process data for PLA experiments
def PLA_data(dfsmall, treatment_ID):
    counter = 0
    lwholeCell = []
    for index,row in dfsmall.iterrows():
        area = row["area"]
        sphase_filters = row["Sphase_filter"]
        area_filters = row["area_filter"]
        imageNr = row["ImageNumb"]
        z_plane = row["Z"]
        c2_median = row["c2_median"]
        focicount = row["c4_FociCount"]
        well_Nr = row["well_ID"]
        tlineCell = (treatment_ID, imageNr, z_plane, well_Nr, sphase_filters, area_filters, area, c2_median, focicount)
        lwholeCell.append(tlineCell)
        counter = counter+1
        if counter % 10000 == 0 : 
            print("So many lines are done:", counter)
    return(lwholeCell)

            
#read in multiple files and add the data to the database
fileList = []
while True:
    line = input('filepath or "done" ')
    if line == 'done':
        break
    fileList.append(line)

for file in fileList:
    fileReader(file)

#Commit changes and close the database connection
conn.commit()
conn.close()

#next step: use the database to analyse the data
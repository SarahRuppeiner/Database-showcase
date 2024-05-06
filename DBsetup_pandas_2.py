# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 10:52:03 2024

@author: srupp
"""
import sqlite3

#Set up the SQLite database

conn = sqlite3.connect('DB_project.sqlite')
cur = conn.cursor()

#Drop existing tables if they exist and create the desired table layout
cur.executescript("""
DROP TABLE IF EXISTS "filter_sphase";
DROP TABLE IF EXISTS "filter_area";
DROP TABLE IF EXISTS "experiment_type";
DROP TABLE IF EXISTS "treatment_type";
DROP TABLE IF EXISTS "experiment";
DROP TABLE IF EXISTS "treatment";
DROP TABLE IF EXISTS "cell";

                 
CREATE TABLE IF NOT EXISTS "filter_sphase" (
	"id"	TEXT UNIQUE,
	PRIMARY KEY("id")
);    
CREATE TABLE IF NOT EXISTS "filter_area" (
	"id"	TEXT UNIQUE,
	PRIMARY KEY("id")
);   
CREATE TABLE IF NOT EXISTS "experiment_type" (
	"id"	TEXT UNIQUE,
	PRIMARY KEY("id")
);             
CREATE TABLE IF NOT EXISTS "treatment_type" (
	"id"	TEXT UNIQUE,
    "main"  TEXT,
    "sub"  TEXT,
	PRIMARY KEY("id")
);                  
CREATE TABLE IF NOT EXISTS "experiment" (
	"id"	TEXT UNIQUE,
    "experiment_nr" TEXT,
	"etype_id"	TEXT,
	PRIMARY KEY("id"),
	FOREIGN KEY("etype_id") REFERENCES "experiment_type"("id")
);
CREATE TABLE IF NOT EXISTS "treatment" (
	"id"	TEXT UNIQUE,
	"experiment_id"	TEXT,
	"ttype_id"	TEXT,
    PRIMARY KEY("id"),
	FOREIGN KEY("experiment_id") REFERENCES "Experiment"("id"),
    FOREIGN KEY("ttype_id") REFERENCES "treatment_type"("id")
);
CREATE TABLE IF NOT EXISTS "cell" (
	"id"	INTEGER UNIQUE,
	"image_nr"	INTEGER,
	"z_plane"	INTEGER,
	"well_Nr"	INTEGER,
    "treatment_id" TEXT,
	"filter_sphase"	TEXT,
	"filter_area"	TEXT,
	"area"	NUMERIC,
	"c2_median"	NUMERIC,
	"foci_count"	INTEGER,
	FOREIGN KEY("filter_sphase") REFERENCES "filter_sphase"("id"),
	FOREIGN KEY("filter_area") REFERENCES "filter_area"("id"),
	FOREIGN KEY("treatment_id") REFERENCES "treatment"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
) 
""")

conn.commit()   
print("setup was successfull")
conn.close()    

#for adding the Data into the database see next script "DB_insertData"

           
                  
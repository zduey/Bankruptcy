"""
Monetary Policy and Bankruptcy
Final Project -- CSC 432
Spring 2013

Zach A Duey
"""
# os.chdir('/home/zduey/Documents/GitHub/Bankruptcy/')


import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
# Read in individual data

d29 = pd.read_csv('1929.csv',sep=';')
d31 = pd.read_csv('1931.csv',sep=';')

# Merge Data
data = pd.concat([d29,d31],ignore_index=True)

# DATA CLEANING

# Selection
names = ['Year','City','County','Name of Concern','Type','Pecuniary Strength','Credit Rating']
data = data[names]
# rename columns for easier selection
d29 = d29.rename(columns={'Name of Concern':'Name','Pecuniary Strength': 'Grade','Credit Rating':'Rating'})
d31 = d31.rename(columns={'Name of Concern':'Name','Pecuniary Strength': 'Grade','Credit Rating':'Rating'})
data = data.rename(columns={'Name of Concern':'Name','Pecuniary Strength': 'Grade','Credit Rating':'Rating'})

# Data Reforming
size = {'Aa':1000000,'A+':750000,'A':500000,'B+':300000,'B':200000,
	'C+':125000,'C':75000,'D+':50000,'D':35000,'E':20000,'F':10000,
	'G':5000,'H':3000,'J':2000,'K':1000,'L':500,'M':0}

data['Size'] = data['Grade'].map(size) # change pecunairy strength to a size variable
data['Year'] = data['Year'].map(lambda x: int(x)) # change year from string to int

# Create binary column for which district the county resides in (Neshoba = Atlanta, Winston = St. Louis
data['Fed_District'] = 0

def set_district(data):
  for obs in range(data.County.size):
    if(data.County[obs] == 'Neshoba'): 
      data.Fed_District[obs] = 1

set_district(data)

# Identify Entrance/Exit of Firms
data['Exit'] = 0 # create new column to track whether a firm exited
data['Name'] = data['Name'].map(lambda x: x.lower()) # turn all names to lower case
data['Name'] = [obs.replace('.','') for obs in data.Name] # remove periods from all names


def firm_exit(y0,y1):
  firms_0 = set(data[data.Year == y0].Name)
  firms_1 = set(data[data.Year == y1].Name)
  exited = firms_0.difference(firms_1)
  entered = firms_1.difference(firms_0)
  errors = []
  for firm in exited:
    for obs in firms_1:
      if(fuzz.ratio(firm,obs) > 80):
	errors.append(firm)
  exited = exited.difference(set(errors))
  for i in range(len(data[data.Year == y0])):
    if (data.Name[i] in exited):
      data.Exit[i] = 1


firm_exit(1929,1931)
num_firms_1929 = len(data[data.Year == 1929]) #335
num_firms_1931 = len(data[data.Year == 1931]) # 283
firms_exited = data.Exit.sum() # 141
firms_entered = num_firms_1931 - (num_firms_1929-firms_exited) # 89
pct_exit = firms_exited/float(num_firms_1929) # 49%

# Exit by Fed District
north_exit = data[data.Fed_District == 0].Exit.sum() # 84
south_exit = data[data.Fed_District == 1].Exit.sum() # 57

grouped = data.groupby(['Year','Size','Exit',])
size = grouped.size()

grouped_credit = data.groupby(['Year','Rating','Exit','Fed_District'])
credit = grouped_credit.size()
# Output Data

size.to_csv('size_data.csv')
credit.to_csv('credit_data.csv')


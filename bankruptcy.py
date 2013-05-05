"""
Monetary Policy and Bankruptcy
Final Project -- CSC 432
Spring 2013

Zach A Duey
"""
import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
import statsmodels.api as sm

# 1. DATA CLEANING
d29 = pd.read_csv('1929.csv',sep=';')
d31 = pd.read_csv('1931.csv',sep=';')
data = pd.concat([d29,d31],ignore_index=True)

## a. data selection
names = ['Year','City','County','Name of Concern','Type','Pecuniary Strength',
         'Credit Rating']
data = data[names]

## b. rename columns to single word names
data = data.rename(columns={'Name of Concern':'Name','Pecuniary Strength':
                            'Grade','Credit Rating':'Rating'})

## c. remapping to numerical values where appropriate
size = {'Aa':1000000,'A+':750000,'A':500000,'B+':300000,'B':200000,
	'C+':125000,'C':75000,'D+':50000,'D':35000,'E':20000,'F':10000,
	'G':5000,'H':3000,'J':2000,'K':1000,'L':500,'M':0}
data['Size'] = data['Grade'].map(size)
data['Year'] = data['Year'].map(lambda x: int(x))# years to int values
data['Rating'] = data['Rating'].replace('A1',.5) # letter rating to number
data['Rating'] = data['Rating'].map(lambda x: float(x)) #ratings to floats

## d. create binary column for which district the county resides (Neshoba =1)
Atlanta, Winston = St. Louis
data['Fed_District'] = 0
def set_district(data):
  for obs in range(data.County.size):
    if(data.County[obs] == 'Neshoba'): 
      data.Fed_District[obs] = 1
set_district(data)

## e. identify firms that enter and exit
data['Exit'] = 0 # create new column to track whether a firm exited
data['Entered'] = 0 # create new column to track whether a firm entered
data['Name'] = data['Name'].map(lambda x: x.lower()) # firm names to lowercase
data['Name'] = [obs.replace('.','') for obs in data.Name] # remove periods

def firm_exit(y0,y1):
  firms_0 = set(data[data.Year == y0].Name) #set of firms in y0
  firms_1 = set(data[data.Year == y1].Name) # set of firms in y1
  exited = firms_0.difference(firms_1) # calculates initial difference
  errors = [] # empty array to capture 
  for firm in exited:
    for obs in firms_1:
      if(fuzz.ratio(firm,obs) > 80): # checks for over 80% string match
	errors.append(firm) # if over 80, adds firm to error list
  exited = exited.difference(set(errors)) # takes firms in errors out of exited
  for i in range(len(data[data.Year == y0])):
    if (data.Name[i] in exited):
      data.Exit[i] = 1 # changes exit column to a 1 for firms in exited list


def firm_entrance(y0,y1):
  firms_0 = set(data[data.Year == y0].Name)
  firms_1 = set(data[data.Year == y1].Name)
  entered = firms_1.difference(firms_0)
  errors = []
  for firm in entered:
    for obs in firms_0:
      if(fuzz.ratio(firm,obs) > 80):
	errors.append(firm)
  entered = entered.difference(set(errors))
  for i in range(len(data[data.Year== y0]),len(data[data.Year== y0])+
		 len(data[data.Year == y1])):
    if (data.Name[i] in entered):
      data.Entered[i] = 1
      
# 2. Data Compilation and Analysis

## a. Summary Data
firm_exit(1929,1931)
firm_entrance(1929,1931)
num_firms_1929 = len(data[data.Year == 1929]) #firms in 1929: 335
num_firms_1931 = len(data[data.Year == 1931]) #firms in 1931: 283
firms_exited = data.Exit.sum() # firms exited between 1929-1931: 141
firms_entered = num_firms_1931 - (num_firms_1929-firms_exited)# 89 firms enter
pct_exit = firms_exited/float(num_firms_1929) # 49%
pct_entered = firms_entered/float(num_firms_1931) # 31%
north_exit = data[data.Fed_District == 0].Exit.sum() # 84
south_exit = data[data.Fed_District == 1].Exit.sum() # 57
north_entered = data[data.Fed_District == 0].Entered.sum() #49
south_entered = data[data.Fed_District == 1].Entered.sum() # 46

## b. Grouped Data
grouped = data.groupby(['Year','Size','Exit','Fed_District'])
size = grouped.size()

grouped_credit = data.groupby(['Year','Rating','Exit','Fed_District'])
credit = grouped_credit.size()

grouped_city = data.groupby(['Year','City','Fed_District','Exit',])
city = grouped_city.size()

size.to_csv('size_exit.csv')
credit.to_csv('credit_exit.csv')
city.to_csv('city_exit.csv')

grouped = data.groupby(['Year','Size','Entered','Fed_District',])
size = grouped.size()

grouped_credit = data.groupby(['Year','Rating','Entered','Fed_District'])
credit = grouped_credit.size()

grouped_city = data.groupby(['Year','City','Fed_District','Entered',])
city = grouped_city.size()
# Output Data

size.to_csv('size_entered.csv')
credit.to_csv('credit_entered.csv')
city.to_csv('city_entered.csv')

# Final Data Table
data.to_csv('final_data.csv')


# 3. Logit Models of Entrance and Exit

## a. Logit Model for Exit
logit_exog = data[data.Year == 1929]
logit_exog = logit_exog[['Size','Rating','Fed_District','Exit']]
logit_exog = logit_exog.dropna()
logit_exog.to_csv('logit_exog_data.csv',header=['Size','Rating','Fed_District','Exit'])
logit_endog = logit_exog['Exit']
logit_exog = logit_exog[['Size','Rating','Fed_District']]

mod = sm.Logit(logit_endog,logit_exog)
res_exit = mod.fit()
res_exit.summary()

## b. Logit Model for Entrance
logit_exog = data[data.Year == 1931]
logit_exog = logit_exog[['Size','Rating','Fed_District','Entered']]
logit_exog = logit_exog.dropna()
logit_exog.to_csv('logit_exog_data.csv',header=['Size','Rating','Fed_District','Entered'])
logit_endog = logit_exog['Entered']
logit_exog = logit_exog[['Size','Rating','Fed_District']]

mod = sm.Logit(logit_endog,logit_exog)
res_entrance = mod.fit()
res_entrance.summary()

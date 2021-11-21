# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 08:57:30 2016

@author: lemitri
"""

#%%

import json             
import os
import pandas as pd
import scipy.stats as sp
import matplotlib.pyplot as plt
import seaborn as sb
sb.set_style('ticks')
import itertools as it
import numpy as np
from collections import Counter


def pws_initialize(CS_number,D_day_1,D_day_2=None):
    #D_day_1 (eg D_day_1= '4/12/2017' ( in the form month/day/year)) is the first day to consider and D_day_2 is the last day to consider (included!)   
    #loads data for each hour of this day for market clearing
    #deterministic: single value prediction
    
    if D_day_2 is None:
        D_day_2 = D_day_1    # each day solve the market fr 24h - day 1 start solving and day 2 stop solving (if day2==day1, then you solve for 1 day sequentially) 

    pws_data = {}
    
    input_system_data = pd.read_csv('data/CS_{0}/input_system_data.csv'.format(CS_number))
    gen_data = pd.read_csv('data/CS_{0}/input_gen_data.csv'.format(CS_number)) 
    load_data = pd.read_csv('data/CS_{0}/input_load_data.csv'.format(CS_number))
    time_series = pd.read_csv('data/CS_{0}/input_time_series.csv'.format(CS_number))   # (0-1)*capacity
        
    pws_data['system'] = {}     
    
    pws_data['system']['MODELS'] = ['integrated','hierarchical','decoupled']
    pws_data['system']['DAYS_ALL'] = [index for index in input_system_data['DATE']]
    pws_data['system']['DAYS'] = [pws_data['system']['DAYS_ALL'][index] for index in range(pws_data['system']['DAYS_ALL'].index(D_day_1),pws_data['system']['DAYS_ALL'].index(D_day_2)+1)]
    pws_data['system']['HOURS'] = [input_system_data['HOUR'][index] for index in range(24)] 
    pws_data['system']['TIME_IDS_ALL'] = [index for index in time_series['TIME ID']]
    pws_data['system']['TIME_IDS'] = [input_system_data['TIME ID'][pws_data['system']['HOURS'].index(index2) + 24*pws_data['system']['DAYS_ALL'].index(index1)] for index1 in pws_data['system']['DAYS'] for index2 in pws_data['system']['HOURS'] ]
    pws_data['system']['TIME_DATES'] = {input_system_data['TIME ID'][pws_data['system']['HOURS'].index(index2) + 24*pws_data['system']['DAYS_ALL'].index(index1)]: [index1,index2] for index1 in pws_data['system']['DAYS'] for index2 in pws_data['system']['HOURS'] }
    pws_data['system']['DATES_TIME'] = {(index1,index2):input_system_data['TIME ID'][pws_data['system']['HOURS'].index(index2) + 24*pws_data['system']['DAYS_ALL'].index(index1)] for index1 in pws_data['system']['DAYS'] for index2 in pws_data['system']['HOURS'] }    
    pws_data['system']['GENERATORS'] = [index for index in gen_data['ID']]
    pws_data['system']['LOADS'] = [index for index in load_data['ID']]
    
    gen_data = pd.read_csv('data/CS_{0}/input_gen_data.csv'.format(CS_number),index_col='ID') 
    load_data = pd.read_csv('data/CS_{0}/input_load_data.csv'.format(CS_number),index_col='ID')
    time_series = pd.read_csv('data/CS_{0}/input_time_series.csv'.format(CS_number),index_col='TIME ID')
    
    pws_data['gen'] = {gen:{} for gen in pws_data['system']['GENERATORS']}
    
    for gen in  pws_data['system']['GENERATORS']: # for each generator define parameters
        
        pws_data['gen'][gen]['ID'] = gen
        pws_data['gen'][gen]['TYPE'] = gen_data['TYPE'][gen]
        pws_data['gen'][gen]['SUBTYPE'] = gen_data['SUBTYPE'][gen]
        pws_data['gen'][gen]['E_MAX'] = gen_data['E_MAX'][gen]
        pws_data['gen'][gen]['E_MIN'] = gen_data['E_MIN'][gen]
        pws_data['gen'][gen]['H_MAX'] = gen_data['H_MAX'][gen]
        pws_data['gen'][gen]['H_MIN'] = gen_data['H_MIN'][gen]
        pws_data['gen'][gen]['C_E'] = gen_data['C_E'][gen]   # cost for providing elec energy
        pws_data['gen'][gen]['C_H'] = gen_data['C_H'][gen]   # cost for providing heat energy
        pws_data['gen'][gen]['EFF_CH'] = gen_data['EFF_CH'][gen] #charging efficiency
        pws_data['gen'][gen]['EFF_DIS'] = gen_data['EFF_DIS'][gen] #discharging efficiency 
        pws_data['gen'][gen]['S_MAX'] = gen_data['S_MAX'][gen] #max energy stored for batteries and heat tanks
        pws_data['gen'][gen]['CH_MAX'] = gen_data['CH_MAX'][gen] 
        pws_data['gen'][gen]['DIS_MAX'] = gen_data['DIS_MAX'][gen]
        pws_data['gen'][gen]['COP'] = gen_data['COP'][gen] #COP for heat pumps 
        pws_data['gen'][gen]['R'] = gen_data['R'][gen] #min heat/elec ratio for CHPs
        pws_data['gen'][gen]['EFF_H'] = gen_data['EFF_H'][gen] # heat prod efficiency for CHPs
        pws_data['gen'][gen]['EFF_E'] = gen_data['EFF_E'][gen] # elec prod efficiency for CHPs
        pws_data['gen'][gen]['F_MAX'] = gen_data['F_MAX'][gen] #max fuel intake for CHP 
        pws_data['gen'][gen]['S_INIT'] = gen_data['S_INIT'][gen] #initial energy stored
        
    pws_data['load'] = {load:{} for load in pws_data['system']['LOADS']}
    
    for load in pws_data['system']['LOADS']: 
        
        pws_data['load'][load]['ID'] = load  
        pws_data['load'][load]['TYPE'] = load_data['TYPE'][load]
        pws_data['load'][load]['CAPACITY'] = load_data['CAPACITY'][load]
        pws_data['load'][load]['VOLL'] = load_data['VOLL'][load]
        pws_data['load'][load]['TIME_ID_SERIES']={index:pws_data['load'][load]['CAPACITY']*time_series['SERIES {0}'.format(load)][index]  for index in pws_data['system']['TIME_IDS']}   
        pws_data['load'][load]['DATE_SERIES']={(pws_data['system']['TIME_DATES'][index][0],pws_data['system']['TIME_DATES'][index][1]):pws_data['load'][load]['CAPACITY']*time_series['SERIES {0}'.format(load)][index]  for index in pws_data['system']['TIME_IDS']}   
        
        
    pws_data['system']['ELECTRICITY LOADS'] = []
    pws_data['system']['HEAT LOADS'] = []  
    
    for load in pws_data['system']['LOADS']:               
        if pws_data['load'][load]['TYPE'] == 'HEAT':       
           pws_data['system']['HEAT LOADS'].append(load)
        if pws_data['load'][load]['TYPE'] == 'ELECTRICITY':       
           pws_data['system']['ELECTRICITY LOADS'].append(load)
    
    pws_data['system']['ELECTRICITY GENERATORS'] = []
    pws_data['system']['SYNCHRONOUS GENERATORS'] = []
    pws_data['system']['RENEWABLE GENERATORS'] = []
    pws_data['system']['HEAT GENERATORS'] = []
    pws_data['system']['HEAT ONLY GENERATORS'] = []
    pws_data['system']['HEAT PUMPS'] = []
    pws_data['system']['CHP GENERATORS'] = []
    pws_data['system']['CHP EXTRACTION GENERATORS'] = []
    pws_data['system']['CHP BACKPRESSURE GENERATORS'] = []
    pws_data['system']['STORAGES'] = []
    pws_data['system']['ELECTRICITY STORAGES'] = []   
    pws_data['system']['HEAT STORAGES'] = [] 
    
    for gen in pws_data['system']['GENERATORS']:   
        
        if pws_data['gen'][gen]['TYPE'] == 'ELECTRICITY' or pws_data['gen'][gen]['TYPE'] == 'COMBINED' or pws_data['gen'][gen]['TYPE'] == 'HEAT PUMP':
           pws_data['system']['ELECTRICITY GENERATORS'].append(gen)
        if pws_data['gen'][gen]['SUBTYPE'] == 'RENEWABLE':       
           pws_data['system']['RENEWABLE GENERATORS'].append(gen)
        if pws_data['gen'][gen]['SUBTYPE'] == 'SYNCHRONOUS':       
           pws_data['system']['SYNCHRONOUS GENERATORS'].append(gen) 
           
        if pws_data['gen'][gen]['TYPE'] == 'HEAT' or pws_data['gen'][gen]['TYPE'] == 'COMBINED' or pws_data['gen'][gen]['TYPE'] == 'HEAT PUMP':        
           pws_data['system']['HEAT GENERATORS'].append(gen)
        if pws_data['gen'][gen]['SUBTYPE'] == 'HEAT ONLY':
           pws_data['system']['HEAT ONLY GENERATORS'].append(gen)  
        if pws_data['gen'][gen]['TYPE'] == 'HEAT PUMP':
           pws_data['system']['HEAT PUMPS'].append(gen)   
           
        if pws_data['gen'][gen]['TYPE'] == 'COMBINED':
           pws_data['system']['CHP GENERATORS'].append(gen)
        if pws_data['gen'][gen]['SUBTYPE'] == 'BACKPRESSURE':
           pws_data['system']['CHP BACKPRESSURE GENERATORS'].append(gen)
        if pws_data['gen'][gen]['SUBTYPE'] == 'EXTRACTION':
           pws_data['system']['CHP EXTRACTION GENERATORS'].append(gen)
        
        if pws_data['gen'][gen]['SUBTYPE'] == 'STORAGE':
           pws_data['system']['STORAGES'].append(gen)        
        if pws_data['gen'][gen]['TYPE'] == 'ELECTRICITY' and pws_data['gen'][gen]['SUBTYPE'] == 'STORAGE':
           pws_data['system']['ELECTRICITY STORAGES'].append(gen)           
        if pws_data['gen'][gen]['TYPE'] == 'HEAT' and pws_data['gen'][gen]['SUBTYPE'] == 'STORAGE':
           pws_data['system']['HEAT STORAGES'].append(gen)

                
    pws_data['renewable'] = {gen:{} for gen in pws_data['system']['RENEWABLE GENERATORS']}
    for gen in pws_data['system']['RENEWABLE GENERATORS']:
        pws_data['renewable'][gen]['TIME_ID_SERIES']={index:pws_data['gen'][gen]['E_MAX']*time_series['SERIES {0}'.format(gen)][index]  for index in pws_data['system']['TIME_IDS']}   
        pws_data['renewable'][gen]['DATE_SERIES']={(pws_data['system']['TIME_DATES'][index][0],pws_data['system']['TIME_DATES'][index][1]):pws_data['gen'][gen]['E_MAX']*time_series['SERIES {0}'.format(gen)][index]  for index in pws_data['system']['TIME_IDS']}        
        

    #average cost of energy over one day
    pws_data['system']['C_E_AVERAGE']={D_day:(sum(pws_data['gen'][gen]['C_E']*pws_data['renewable'][gen]['DATE_SERIES'][D_day,hour] for gen in pws_data['system']['RENEWABLE GENERATORS'] for hour in pws_data['system']['HOURS'])+sum(pws_data['gen'][gen]['C_E']*pws_data['gen'][gen]['E_MAX'] for gen in pws_data['system']['SYNCHRONOUS GENERATORS']+pws_data['system']['CHP GENERATORS'] for hour in pws_data['system']['HOURS']))/(sum(pws_data['renewable'][gen]['DATE_SERIES'][D_day,hour] for gen in pws_data['system']['RENEWABLE GENERATORS'] for hour in pws_data['system']['HOURS'])+sum(pws_data['gen'][gen]['E_MAX'] for gen in pws_data['system']['SYNCHRONOUS GENERATORS']+pws_data['system']['CHP GENERATORS'] for hour in pws_data['system']['HOURS'])) for D_day in pws_data['system']['DAYS']}
    pws_data['system']['C_H_AVERAGE']={D_day:sum(pws_data['gen'][gen]['C_H']*pws_data['gen'][gen]['H_MAX'] for gen in pws_data['system']['CHP GENERATORS']+pws_data['system']['HEAT ONLY GENERATORS'] for hour in pws_data['system']['HOURS'])/sum(pws_data['gen'][gen]['H_MAX'] for gen in pws_data['system']['CHP GENERATORS']+pws_data['system']['HEAT ONLY GENERATORS']  for hour in pws_data['system']['HOURS']) for D_day in pws_data['system']['DAYS']}
                 
    pws_results={}
    
    pws_results['system']={model:{} for model in pws_data['system']['MODELS']}

    for model in pws_data['system']['MODELS']:
        pws_results['system'][model]['electricity price'] = {}
        pws_results['system'][model]['heat price'] = {}
        pws_results['system'][model]['electricity system cost'] = {}
        pws_results['system'][model]['heat system cost'] = {}
        pws_results['system'][model]['overall system cost'] = {}
    
    pws_results['gen']={model:{gen:{} for gen in pws_data['system']['GENERATORS']} for model in pws_data['system']['MODELS']}
    
    for model in pws_data['system']['MODELS']:
        
        for gen in pws_data['system']['ELECTRICITY GENERATORS']:
            pws_results['gen'][model][gen]['electricity production'] = {}
        for gen in pws_data['system']['HEAT GENERATORS']:
            pws_results['gen'][model][gen]['heat production'] = {}
            pws_results['gen'][model][gen]['heat bid'] = {}
        for gen in pws_data['system']['STORAGES']:
            pws_results['gen'][model][gen]['charge'] = {}
            pws_results['gen'][model][gen]['discharge'] = {}
            pws_results['gen'][model][gen]['energy stored'] = {}
            pws_results['gen'][model][gen]['energy stored init'] = {D_day_1:gen_data['S_INIT'][gen]}
        for gen in pws_data['system']['HEAT PUMPS']+pws_data['system']['CHP GENERATORS']:
            pws_results['gen'][model][gen]['electricity production min'] = {}
            pws_results['gen'][model][gen]['electricity production max'] = {}
            pws_results['gen'][model][gen]['heat bid accepted'] = {}
            
        #set the heat bids to C_H for heat only generators for all models (and for CHPs and HPs for the integrated model)
        for gen in pws_data['system']['HEAT STORAGES']+pws_data['system']['HEAT ONLY GENERATORS']:
            pws_results['gen'][model][gen]['heat bid'] = {(D_day,hour):pws_data['gen'][gen]['C_H'] for D_day in pws_data['system']['DAYS'] for hour in pws_data['system']['HOURS']}
    for gen in pws_data['system']['HEAT PUMPS']+pws_data['system']['CHP GENERATORS']:        
        pws_results['gen']['integrated'][gen]['heat bid'] = {(D_day,hour):pws_data['gen'][gen]['C_H'] for D_day in pws_data['system']['DAYS'] for hour in pws_data['system']['HOURS']}

    pws_results['load']={model:{load:{} for load in pws_data['system']['LOADS']} for model in pws_data['system']['MODELS']}

    for model in pws_data['system']['MODELS']:
        
        for load in pws_data['system']['LOADS']:
            pws_results['load'][model][load]['load shedding'] = {}
            
    return pws_data, pws_results
          




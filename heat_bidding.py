# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 13:58:40 2021

@author: lmitridati
"""

def marginal_heat_cost(pws_data,electricity_price):
    
    bid = {}
    
    for hour in pws_data['system']['HOURS']:
        
        for gen in pws_data['system']['HEAT PUMPS']:
        
            bid[gen,hour] = electricity_price[hour]/pws_data['gen'][gen]['COP']
        
        for gen in pws_data['system']['CHP GENERATORS']:
            
            bid[gen,hour] = max(pws_data['gen'][gen]['C_H'],pws_data['gen'][gen]['C_H'] + pws_data['gen'][gen]['R']*pws_data['gen'][gen]['C_E'] - electricity_price[hour]*pws_data['gen'][gen]['R'] , electricity_price[hour]*pws_data['gen'][gen]['EFF_H']/pws_data['gen'][gen]['EFF_E']) 
    
    return bid
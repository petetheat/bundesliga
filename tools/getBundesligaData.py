# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 15:30:54 2017

@author: Asus
"""

import json
import requests
import pandas as pd


def getSeason(year, division='bl1'):
    query = 'http://www.openligadb.de/api/getmatchdata/' + division + '/' + str(year)
    r = requests.get(query)

    results = r.json()
    
    return results


def tableInit(results):
    teams = set()
    teamNames = {}
    for game in results:
        teams.add(game['Team1']['TeamId'])
        teams.add(game['Team2']['TeamId'])
        
        teamNames[game['Team1']['TeamId']] = game['Team1']['TeamName']
        teamNames[game['Team2']['TeamId']] = game['Team2']['TeamName']

    return teams, teamNames

def getTable(years):
    
    for year in years:
        results = getSeason(year)
        
        
        
        
results = getSeason(2016)

teams, teamNames = tableInit(results)


print teamNames
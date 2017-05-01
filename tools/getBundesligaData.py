# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 15:30:54 2017

@author: Asus
"""

import json
import requests
import pandas as pd

#%% Helper functions

'''
getSeason: Get results for an entire season from www.openliga.db.de
           Input: year (mandatory), division (optional, if omitted first division)
'''
def getSeason(year, division='bl1'):
    query = 'http://www.openligadb.de/api/getmatchdata/' + division + '/' + str(year)
    r = requests.get(query)

    results = r.json()
    
    return results

'''
tableInit: Initialize table at the beginning of each season
'''
def tableInit(results):
    teams = set()
    teamNames = {}
    for game in results:
        teams.add(game['Team1']['TeamId'])
        teams.add(game['Team2']['TeamId'])
        
        teamNames[game['Team1']['TeamId']] = game['Team1']['TeamName']
        teamNames[game['Team2']['TeamId']] = game['Team2']['TeamName']

    teamDF = pd.DataFrame(list(teams),columns=['TeamId'])
    
    teamDF['pointsTotal'] = 0
    teamDF['pointsHome'] = 0
    teamDF['pointsAway'] = 0
    teamDF['goalsTotal'] = 0
    teamDF['goalsConcededTotal'] = 0
    teamDF['goalsHomeTotal'] = 0
    teamDF['goalsConcededHomeTotal'] = 0
    teamDF['goalsAwayTotal'] = 0
    teamDF['goalsConcededAwayTotal'] = 0
    
    return teamDF, teamNames

'''
getTable: Get table for each game day for all specified years
'''
def getTable(years, division='bl1'):
    
    for year in years:
        results = getSeason(year, division)
        
        table, teamNames = tableInit(results)
        
        for game in results:
            iHome = table.TeamId == game['Team1']['TeamId']
            iAway = table.TeamId == game['Team2']['TeamId']
            
            if game['MatchIsFinished']:
                if game['MatchResults'][0]['ResultTypeID'] == 2:
                    gameResults = game['MatchResults'][0]
                elif game['MatchResults'][1]['ResultTypeID'] == 2:
                    gameResults = game['MatchResults'][1]
                else:
                    print("No end result available")
                
                
                if gameResults['PointsTeam1'] > gameResults['PointsTeam2']:
                    table.loc[iHome, 'pointsTotal'] += 3
                    table.loc[iHome, 'pointsHome'] += 3
                elif gameResults['PointsTeam1'] < gameResults['PointsTeam2']:
                    table.loc[iAway, 'pointsTotal'] += 3
                    table.loc[iAway, 'pointsAway'] += 3
                else:
                    table.loc[iHome, 'pointsTotal'] += 1
                    table.loc[iHome, 'pointsHome'] += 1
                    table.loc[iAway, 'pointsTotal'] += 1
                    table.loc[iAway, 'pointsAway'] += 1
                
                table.loc[iHome, 'goalsTotal'] += gameResults['PointsTeam1']
                table.loc[iAway, 'goalsTotal'] += gameResults['PointsTeam2']
                table.loc[iHome, 'goalsConcededTotal'] += gameResults['PointsTeam2']
                table.loc[iAway, 'goalsConcededTotal'] += gameResults['PointsTeam1']
                table.loc[iHome, 'goalsHomeTotal'] += gameResults['PointsTeam1']
                table.loc[iAway, 'goalsAwayTotal'] += gameResults['PointsTeam2']
                table.loc[iHome, 'goalsConcededHomeTotal'] += gameResults['PointsTeam2']
                table.loc[iAway, 'goalsConcededAwayTotal'] += gameResults['PointsTeam1']
    
                
                table['goalDiff'] = table.goalsTotal - table.goalsConcededTotal
                table = table.sort_values(by=["pointsTotal", "goalDiff", "goalsTotal"], ascending=[False, False, False])
                
                print table[['TeamId', 'pointsTotal']]
            
            else:
                print("Game not played yet")
    
        
    
    return table, teamNames

#%%

table, tableNames = getTable([2016])

print table
print tableNames

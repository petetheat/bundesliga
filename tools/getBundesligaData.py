# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 15:30:54 2017

@author: Asus
"""

import json
import requests
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

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
    
    teamDF['gameDay'] = 0
    teamDF['standing'] = range(1,19,1)
    
    return teamDF, teamNames

'''
getTable: Get table for each game day for all specified years
'''
def getTable(results, gameDay=34):
    
    table, teamNames = tableInit(results)
    
    for game in results:
        iHome = table.TeamId == game['Team1']['TeamId']
        iAway = table.TeamId == game['Team2']['TeamId']
        
        if (game['MatchIsFinished']) and (game['Group']['GroupOrderID'] <= gameDay):
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

            table.loc[iAway, 'gameDay'] = game['Group']['GroupOrderID']
            table.loc[iHome, 'gameDay'] = game['Group']['GroupOrderID']
            
            table['goalDiff'] = table.goalsTotal - table.goalsConcededTotal
            table = table.sort_values(by=["pointsTotal", "goalDiff", "goalsTotal"], ascending=[False, False, False])
            
            table['standing'] = range(1,19,1)
    
    return table, teamNames

'''

'''
def getOutput(years, division='bl1'):
    for year in years:
        results = getSeason(year, division)
        
        currentGameDay = 0
        
        columns = ['Season', 'Game Day', 'Team1', 'Team2', 'Standing1', 'Standing2', 'Points1', 'Points2', 'PointsHome1', 'PointsAway2', 'Goals1', 'Goals2', 'Goals Conceded1', 'Goals Conceded2', 'Result']
        
        df = pd.DataFrame(columns=columns)
        
        season = []
        gameDay = []
        team1 = []
        team2 = []
        standing1 = []
        standing2 = []
        points1 = []
        points2 = []
        pointsHome1 = []
        pointsAway2 = []
        goals1 = []
        goals2 = []
        goalsconceded1 = []
        goalsconceded2 = []
        result = []
        
        for game in results:
            if game['Group']['GroupOrderID'] > currentGameDay:
                currentGameDay = game['Group']['GroupOrderID']
                table, teamNames = getTable(results, currentGameDay-1)
            
            season.append(year)
            gameDay.append(currentGameDay)
            team1.append(game['Team1']['TeamId'])
            team2.append(game['Team2']['TeamId'])
            
            standing1.append(pd.np.array(table.loc[table.TeamId == game['Team1']['TeamId'], 'standing'])[0])
            standing2.append(pd.np.array(table.loc[table.TeamId == game['Team2']['TeamId'], 'standing'])[0])
            
            points1.append(pd.np.array(table.loc[table.TeamId == game['Team1']['TeamId'], 'pointsTotal'])[0])
            points2.append(pd.np.array(table.loc[table.TeamId == game['Team2']['TeamId'], 'pointsTotal'])[0])
            
            pointsHome1.append(pd.np.array(table.loc[table.TeamId == game['Team1']['TeamId'], 'pointsHome'])[0])
            pointsAway2.append(pd.np.array(table.loc[table.TeamId == game['Team2']['TeamId'], 'pointsAway'])[0])
            
            goals1.append(pd.np.array(table.loc[table.TeamId == game['Team1']['TeamId'], 'goalsTotal'])[0])
            goals2.append(pd.np.array(table.loc[table.TeamId == game['Team2']['TeamId'], 'goalsTotal'])[0])
            
            goalsconceded1.append(pd.np.array(table.loc[table.TeamId == game['Team1']['TeamId'], 'goalsConcededTotal'])[0])
            goalsconceded2.append(pd.np.array(table.loc[table.TeamId == game['Team2']['TeamId'], 'goalsConcededTotal'])[0])
            
            if game['MatchIsFinished']:
                if game['MatchResults'][0]['ResultTypeID'] == 2:
                    gameResults = game['MatchResults'][0]
                elif game['MatchResults'][1]['ResultTypeID'] == 2:
                    gameResults = game['MatchResults'][1]
                
                if gameResults['PointsTeam1'] > gameResults['PointsTeam2']:
                    result.append(1)
                elif gameResults['PointsTeam1'] < gameResults['PointsTeam2']:
                    result.append(3)
                else:
                    result.append(2)
            else:
                result.append(np.nan)
            
            
            
        df['Season'] = season
        df['Game Day'] = gameDay
        df['Team1'] = team1
        df['Team2'] = team2
        df['Standing1'] = standing1
        df['Standing2'] = standing2
        df['Points1'] = points1
        df['Points2'] = points2
        df['PointsHome1'] = pointsHome1
        df['PointsAway2'] = pointsAway2
        df['Goals1'] = goals1
        df['Goals2'] = goals2
        df['Goals Conceded1'] = goalsconceded1
        df['Goals Conceded2'] = goalsconceded2
        df['Result'] = result
            
    return df

#%%

df1 = getOutput([2013])
df2 = getOutput([2014])
df3 = getOutput([2015])
df4 = getOutput([2016])

df = pd.DataFrame()

df = df.append(df1, ignore_index=True)
df = df.append(df2, ignore_index=True)
df = df.append(df3, ignore_index=True)
df = df.append(df4, ignore_index=True)

#%%
plt.figure(figsize=(10,5))
df.plot.scatter(x='PointsHome1', y='PointsAway2', s=50, c='Result', colormap='Spectral', figsize=(20,10))


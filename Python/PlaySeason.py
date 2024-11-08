import pandas as pd
from Python.Team import Team
from Python.TeamName import *
from Python.PlayGame import Game
import pickle
import os
import time

class Season:
    def __init__(self, team):
        self.wins=0
        self.losses=0
        self.totalWins=0
        self.totalLosses=0
        self.team = team
        self.hitters = pd.read_csv('Data/Hitters2024.csv') # Read hitters csv
        self.pitchers = pd.read_csv('Data/Pitchers2024.csv') # Read pitchers csv
        self.hittersPitches = pd.read_csv('Data/HittersPitches2024.csv') # REad hitters pitches csv
        self.pitchersPitches = pd.read_csv('Data/PitchersPitches2024.csv') # Read pitchers pitches csv
        self.teamCache = self.loadTeamCache()

    def loadTeamCache(self):
        """Load cached teams from a file."""
        if os.path.exists('team_cache.pkl'):
            with open('team_cache.pkl', 'rb') as f:
                return pickle.load(f)
        return {}
    
    def saveTeamCache(self, cache):
        """Save the team cache to a file."""
        with open('team_cache.pkl', 'wb') as f:
            pickle.dump(cache, f)

    def getTeam(self, name):
        if name in self.teamCache:
            return self.teamCache[name]
        else:
            print("Creating Team")
            team = Team(name)
            teamHitters = self.hitters[self.hitters['Team'] == name]
            teamHitters = teamHitters[teamHitters['PA'] > 0] # Make sure hitters have at least 1 plate appearance
            teamPitchers = self.pitchers[self.pitchers['Team'] == name]
            teamPitchers = teamPitchers[teamPitchers['BF'] > 20] # Make sure pitchers have at least 20 batters faced
            teamPitchersPitches = self.pitchersPitches[self.pitchersPitches['Tm'] == name]
            teamPitchersPitches = teamPitchersPitches[teamPitchersPitches['PA'] > 0] # Make sure hitters have at least 1 plate appearance
            teamHittersPitches = self.hittersPitches[self.hittersPitches['Tm'] == name]
            teamHittersPitches = teamHittersPitches[teamHittersPitches['PA'] > 0] # Make sure hitters have at least 1 plate appearance
            team.fillLineupTest(teamHitters, teamHittersPitches)
            team.fillPitchingStaff(teamPitchers, teamPitchersPitches)

            self.teamCache[name] = team
            self.saveTeamCache(self.teamCache)
            self.teamCache = self.loadTeamCache()
            return team

    def getCurrentSimulationState(self):
        currentSimState = {
            'sim_game': False,
            'end_sim': False,
            'team': self.team.name,
            'wins': self.wins,
            'losses': self.losses
        }
        return currentSimState

    def simSeason(self, update_callback, waitForNextBatter):
        schedule = pd.read_csv('Data/2024MLBSchedule.csv')
        curTime = time.time()
        name = getRealName(self.team.name)
        schedule = schedule[(schedule['Visitor'] == name) | (schedule['Home'] == name)]
        self.wins = 0
        self.losses = 0
        for index, row in schedule.iterrows():
            teamInput = getAbbreviation(row['Visitor'] if row['Home']==name else row['Home'])
            otherTeam = self.getTeam(teamInput)
            awayTeam = self.team if getAbbreviation(row['Visitor'])==self.team.name else otherTeam
            homeTeam = self.team if getAbbreviation(row['Home'])==self.team.name else otherTeam

            game = Game(awayTeam, homeTeam, True)
            winner = game.playGame(update_callback, waitForNextBatter)
            if(winner==self.team):
                self.wins+=1
                self.totalWins+=1
            else:
                self.losses+=1
                self.totalLosses+=1
            # update_callback(self.getCurrentSimulationState())
            # timeGame += time.time() - curTime
            # print(str(winner.name))
        # print(f'Time : {self.time}')
        # curTime = time.time()
        # print(f'Wins: {self.wins}\nLosses: {self.losses}')
        return (self.wins, self.losses)
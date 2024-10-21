import pandas as pd
from Python.Team import Team
from Python.TeamName import *
from Python.PlayGame import Game
import time
class Season:
    def __init__(self, team):
        self.wins=0
        self.losses=0
        self.team = team
        self.hitters = pd.read_csv('Data/Hitters2024.csv') # Read hitters csv
        self.pitchers = pd.read_csv('Data/Pitchers2024.csv') # Read pitchers csv
        self.hittersPitches = pd.read_csv('Data/HittersPitches2024.csv') # REad hitters pitches csv
        self.pitchersPitches = pd.read_csv('Data/PitchersPitches2024.csv') # Read pitchers pitches csv

    def simSeason(self, update_callback, waitForNextBatter):
        schedule = pd.read_csv('Data/2024MLBSchedule.csv')
        name = getRealName(self.team.name)
        # team1Hitters = hitters[hitters['Team'] == team1Input]
        schedule = schedule[(schedule['Visitor'] == name) | (schedule['Home'] == name)]
        # print(schedule)
        for index, row in schedule.iterrows():
            # print(row)
            teamInput = getAbbreviation(row['Visitor'] if row['Home']==name else row['Home'])
            otherTeamHitters = self.hitters[self.hitters['Team'] == teamInput]
            otherTeamHitters = otherTeamHitters[otherTeamHitters['PA'] > 0] # Make sure hitters have at least 1 plate appearance
            otherTeamPitchers = self.pitchers[self.pitchers['Team'] == teamInput]
            otherTeamPitchers = otherTeamPitchers[otherTeamPitchers['BF'] > 20] # Make sure pitchers have at least 20 batters faced
            otherTeamPitchersPitches = self.pitchersPitches[self.pitchersPitches['Tm'] == teamInput]
            otherTeamPitchersPitches = otherTeamPitchersPitches[otherTeamPitchersPitches['PA'] > 0] # Make sure hitters have at least 1 plate appearance
            otherTeamHittersPitches = self.hittersPitches[self.hittersPitches['Tm'] == teamInput]
            otherTeamHittersPitches = otherTeamHittersPitches[otherTeamHittersPitches['PA'] > 0] # Make sure hitters have at least 1 plate appearance
            otherTeam = Team(teamInput)
            otherTeam.fillLineupTest(otherTeamHitters, otherTeamHittersPitches)
            otherTeam.fillPitchingStaff(otherTeamPitchers, otherTeamPitchersPitches)
            awayTeam = self.team if getAbbreviation(row['Visitor'])==self.team.name else otherTeam
            homeTeam = self.team if getAbbreviation(row['Home'])==self.team.name else otherTeam
            game = Game(awayTeam, homeTeam, True)
            winner = game.playGame(update_callback, waitForNextBatter)
            if(winner==self.team):
                self.wins+=1
            else:
                self.losses+=1
            # print(str(winner.name))
        # print(f'Wins: {self.wins}\nLosses: {self.losses}')
        return (self.wins, self.losses)
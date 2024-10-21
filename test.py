from Python.PlaySeason import Season
from Python.Team import Team
import pandas as pd
def update_callback(currentState):
    return

def waitForNextBatter():
    return


teamInput = "NYY"
hitters = pd.read_csv('Data/Hitters2024.csv') # Read hitters csv
pitchers = pd.read_csv('Data/Pitchers2024.csv') # Read pitchers csv
hittersPitches = pd.read_csv('Data/HittersPitches2024.csv') # REad hitters pitches csv
pitchersPitches = pd.read_csv('Data/PitchersPitches2024.csv') # Read pitchers pitches csv
team1Hitters = hitters[hitters['Team'] == teamInput]
team1Hitters = team1Hitters[team1Hitters['PA'] > 0] # Make sure hitters have at least 1 plate appearance
team1Pitchers = pitchers[pitchers['Team'] == teamInput]
team1Pitchers = team1Pitchers[team1Pitchers['BF'] > 20] # Make sure pitchers have at least 20 batters faced
team1PitchersPitches = pitchersPitches[pitchersPitches['Tm'] == teamInput]
team1PitchersPitches = team1PitchersPitches[team1PitchersPitches['PA'] > 0] # Make sure hitters have at least 1 plate appearance
team1HittersPitches = hittersPitches[hittersPitches['Tm'] == teamInput]
team1HittersPitches = team1HittersPitches[team1HittersPitches['PA'] > 0] # Make sure hitters have at least 1 plate appearance
team1 = Team(teamInput)
team1.fillLineupTest(team1Hitters, team1HittersPitches)
team1.fillPitchingStaff(team1Pitchers, team1PitchersPitches)
wins = 0
losses = 0
season = Season(team1)
record = season.simSeason(update_callback, waitForNextBatter)
print(record)
wins += record[0]
losses += record[1]
# avgWins = wins/1000
# avgLosses = losses/1000
# print(f'Wins: {avgWins}\nLosses: {avgLosses}')

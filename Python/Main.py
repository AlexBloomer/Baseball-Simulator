# python_code/main_simulation.py

from enum import Enum
import pandas as pd
import random
from Python.PositionPlayer import *
from Python.Bases import Bases
from Python.PlayGame import Game
from Python.Team import Team  # Adjust this import based on where Team.py is
from datetime import datetime
import msvcrt

def run_simulation(team1, team2, numSims, update_callback, wait_for_user_callback):
    global current_simulation_state
    # hitters = pd.read_csv('Data/Hitters2024.csv')
    # pitchers = pd.read_csv('Data/Pitchers2024.csv')

    # # Make teams
    # team1Hitters = hitters[hitters['Team'] == team1Input]
    # team2Hitters = hitters[hitters['Team'] == team2Input]
    # team1Pitchers = pitchers[pitchers['Team'] == team1Input]
    # team2Pitchers = pitchers[pitchers['Team'] == team2Input]
    # team1 = Team(team1Input)
    # team2 = Team(team2Input)
    # team1.fillLineup(team1Hitters)
    # team2.fillLineup(team2Hitters)
    # team1.fillPitchingStaff(team1Pitchers)
    # team2.fillPitchingStaff(team2Pitchers)

    # team1.totalRuns, team2.totalRuns = 0, 0
    # team1.wins, team2.wins = 0, 0
    print('before')
    game = Game(team1, team2, numSims > 2)  # Simulate the entire game
    print('after')

    for i in range(int(numSims)):
        winner = game.playGame(update_callback,wait_for_user_callback)
        team1.totalRuns += game.getRuns1()
        team2.totalRuns += game.getRuns2()

        if winner == team1:
            team1.wins += 1
        else:
            team2.wins += 1
        if numSims < 3 or (i+1)%1000 == 0:
            current_simulation_state = {
                'current_simulation_number': i+1,
                'team1_total_runs': team1.totalRuns,
                'team2_total_runs': team2.totalRuns,
                'team1_wins': team1.wins,
                'team2_wins': team2.wins,
                'team1_name': team1.name,
                'team2_name': team2.name,
                'runners': {},
                'gameOver': False
            }

            # Call the callback function to notify about the update
            update_callback(current_simulation_state)
   

    print('end')
    current_simulation_state = {
        'current_simulation_number': i + 1,
        'team1_total_runs': team1.totalRuns,
        'team2_total_runs': team2.totalRuns,
        'team1_wins': team1.wins,
        'team2_wins': team2.wins,
        'team1_name': team1.name,
        'team2_name': team2.name,
        'runners': {},
        'gameOver': True
    }

    # Call the callback function to notify about the update
    update_callback(current_simulation_state)
    results = {
        'team1_name': team1.name,
        'team2_name': team2.name,
        'team1_wins': team1.wins,
        'team2_wins': team2.wins,
        'team1_runs': team1.runs,
        'team2_runs': team2.runs,
        'team1_total_runs': team1.totalRuns,
        'team2_total_runs': team2.totalRuns,
        'team1_results': team1.getPlayerResults(),
        'team2_results': team2.getPlayerResults(),
        'gameOver': True
    }

    return results

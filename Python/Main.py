# python_code/main_simulation.py
from Python.PositionPlayer import *
from Python.PlayGame import Game
import time

def run_simulation(team1, team2, numSims, update_callback, wait_for_user_callback):
    global current_simulation_state
    game = Game(team1, team2, numSims > 2)  # Simulate the entire game
    lastTime = time.time()
    totTime = 0
    print('A')
    for i in range(int(numSims)):
        if((i+1)%1000 == 0):
            totTime += time.time() - lastTime
            print(f'SIMULATION {i+1}: {time.time() - lastTime}')
            lastTime = time.time()
        winner = game.playGame(update_callback,wait_for_user_callback)
        team1.totalRuns += game.getRuns1()
        team2.totalRuns += game.getRuns2()

        if winner == team1:
            team1.wins += 1
        else:
            team2.wins += 1
        if numSims < 3 or (i+1)%500 == 0:
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
    print(f'AVG Time per 1000: {totTime/10}')


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
        'gameOver': True
    }

    return results

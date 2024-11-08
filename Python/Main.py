# python_code/main_simulation.py
from Python.PositionPlayer import *
from Python.PlayGame import Game
from Python.PlaySeason import Season
import time

def simulateGames(team1, team2, numSims, update_callback, waitForNextBatter):
    """ Main function that runs the simulation
        Args:
            team1: Away Team
            team2: Home Team
            numSims: Number of simulations to run
            update_callback: Function to update the JS code with data from python
            waitForNextBatter: Function to wait for user to press button before continuing
    """
    global currentSimState
    game = Game(team1, team2, numSims > 2)  # Create Game object. If more than 2 sims simulate entire thing immediately, otherwise show each play
    
    # Used for logging how long a sim takes
    lastTime = time.time()
    totTime = 0
    print('A')
    
    # For loop which runs the number of sims
    for i in range(int(numSims)):
        # Log how long every 1000 sims takes
        if((i+1)%1000 == 0):
            totTime += time.time() - lastTime
            print(f'SIMULATION {i+1}: {time.time() - lastTime}')
            lastTime = time.time()
        # Play the game
        winner = game.playGame(update_callback,waitForNextBatter)

        # Add how many runs a team scored this game to their total
        team1.totalRuns += game.getRuns1()
        team2.totalRuns += game.getRuns2()

        # Decide winner and add to their total wins
        if winner == team1:
            team1.wins += 1
        else:
            team2.wins += 1
        # Every 500 sims update JS with the information
        if numSims < 3 or (i+1)%500 == 0:
            # update the currentSimState with the new information from the last 500 games
            currentSimState = {
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
            # Call the callback function to notify JS file about the update
            update_callback(currentSimState)

    # log average time per 1000 
    print(f'AVG Time per 1000: {totTime/(numSims/1000)}')

    #  update the currentSimState with the final information
    currentSimState = {
        'sim_game':True,
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
    update_callback(currentSimState)
    
    # Results to be returned to app.py
    results = {
        'sim_game': False,
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

def simulateSeason(team, numSims, update_callback, waitForNextBatter):
    season = Season(team)
    for i in range(numSims):
        record = season.simSeason(update_callback, waitForNextBatter)
        currentSimState = {
            'sim_game': False,
            'end_sim': True,
            'team': team.name,
            'wins': season.wins,
            'losses': season.losses,
            'average_wins': season.totalWins/(i+1),
            'average_losses': season.totalLosses/(i+1)
        }
        update_callback(currentSimState)
    currentSimState = {
        'sim_game': False,
        'end_sim': True,
        'team': team.name,
        'wins': season.wins,
        'losses': season.losses,
        'average_wins': season.totalWins/numSims,
        'average_losses': season.totalLosses/numSims
    }
    update_callback(currentSimState)
    

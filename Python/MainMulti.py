from multiprocessing import Pool
from Python.PlayGame import Game
from flask import Flask, request, jsonify
from threading import Thread

app = Flask(__name__)

def run_single_sim(team1, team2, update_callback, wait_for_user_callback):
    """ Run a single simulation of the game and return the winner. """
    print('run single')
    game = Game(team1, team2, sim=False)
    winner = game.playGame(update_callback, wait_for_user_callback)  # No callbacks in this mode
    return 1 if winner == team1 else 2  # Return 1 for team1 wins, 2 for team2 wins

def run_simulation(team1, team2, numSims, update_callback, wait_for_user_callback):
    """ Run multiple simulations using multiprocessing. """
    print("run multiple")
    # Create a pool of worker processes
    with Pool() as pool:
        # Each worker will run a single simulation
        results = pool.starmap(run_single_sim, [(team1, team2, update_callback, wait_for_user_callback)] * numSims)

    # Count the number of wins for each team
    team1.wins = results.count(1)
    team2.wins = results.count(2)

    # Final callback to update the UI
    current_simulation_state = {
        'team1_wins': team1.wins,
        'team2_wins': team2.wins,
    }
    update_callback(current_simulation_state)

# @app.route('/run-simulation', methods=['POST'])
# def run_simulation_route():
#     global team1, team2, simInProgress
#     data = request.get_json()
#     if not data:
#         return jsonify({"error": "Invalid data"}), 400  # Return an error if no data is sent

#     if simInProgress:
#         return jsonify({"error": "Simulation already in progress"}), 400

#     # Setup the teams and get numSims from data
#     numSims = data.get("numSims", 100)  # Example: default to 100 simulations

#     thread = Thread(target=run_simulation, args=(team1, team2, numSims, update_callback, wait_for_user_callback))
#     thread.start()

#     simInProgress = True
#     return jsonify({"message": "Simulation started"}), 200

# if __name__ == '__main__':
#     app.run(debug=True)

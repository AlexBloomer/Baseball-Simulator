from flask import Flask, jsonify, request, render_template
from threading import Thread
from Python.Main import run_simulation
from Python.Team import Team
from queue import Queue
import pandas as pd
# from Python.PlayGame import playAtBat
import time
app = Flask(__name__)

current_simulation_state = {}
continueSimulation = False
simInProgress = False
team1 = None
team2 = None
result = None
hitters = pd.read_csv('Data/Hitters2024.csv')
pitchers = pd.read_csv('Data/Pitchers2024.csv')
pitchersPitches = pd.read_csv('Data/PitchersPitches2024.csv')
hittersPitches = pd.read_csv('Data/HittersPitches2024.csv')
# Route for the root URL
@app.route('/')
def index():
    return render_template('index.html')  # Render your main HTML file

@app.route('/run-simulation', methods=['POST'])
def run_simulation_route():
    global team1, team2
    global simInProgress
    global current_simulation_state
    global result
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data"}), 400  # Return an error if no data is sent
    
    if simInProgress:
        return jsonify({"error": "simulation already in progress"}), 400
    
    team1Input = data.get('team1')
    team2Input = data.get('team2')
    numSims = int(data.get('numSims'))
    lineup1 = data.get('lineup1')
    lineup2 = data.get('lineup2')

    # Make teams
    team1Hitters = hitters[hitters['Team'] == team1Input]
    team1Hitters = team1Hitters[team1Hitters['PA'] > 0]
    team2Hitters = hitters[hitters['Team'] == team2Input]
    team2Hitters = team2Hitters[team2Hitters['PA'] > 0]
    team1Pitchers = pitchers[pitchers['Team'] == team1Input]
    team1Pitchers = team1Pitchers[team1Pitchers['BF'] > 20]
    team2Pitchers = pitchers[pitchers['Team'] == team2Input]
    team2Pitchers = team2Pitchers[team2Pitchers['BF'] > 20]
    team1PitchersPitches = pitchersPitches[pitchersPitches['Tm'] == team1Input]
    team1PitchersPitches = team1PitchersPitches[team1PitchersPitches['PA'] > 0]
    team2PitchersPitches = pitchersPitches[pitchersPitches['Tm'] == team2Input]
    team2PitchersPitches = team2PitchersPitches[team2PitchersPitches['PA'] > 0]
    team1HittersPitches = hittersPitches[hittersPitches['Tm'] == team1Input]
    team1HittersPitches = team1HittersPitches[team1HittersPitches['PA'] > 0]
    team2HittersPitches = hittersPitches[hittersPitches['Tm'] == team2Input]
    team2HittersPitches = team2HittersPitches[team2HittersPitches['PA'] > 10]
    team1 = Team(team1Input)
    team2 = Team(team2Input)
    team1.fillLineup(team1Hitters, lineup1, team1HittersPitches)
    team2.fillLineup(team2Hitters, lineup2, team2HittersPitches)
    team1.fillPitchingStaff(team1Pitchers, team1PitchersPitches)
    team2.fillPitchingStaff(team2Pitchers, team2PitchersPitches)

    team1.totalRuns, team2.totalRuns = 0, 0
    team1.wins, team2.wins = 0, 0

    thread = Thread(target=run_simulation, args=(team1, team2, numSims, update_callback, wait_for_user_callback))
    thread.start()

    # thread.join()
    # result = queue.get()
    simInProgress = True
    return jsonify({"message": "Simulation started"}), 200

def update_callback(current_state):
    global current_simulation_state
    current_simulation_state = current_state

@app.route('/simulation-ended', methods=['POST'])
def simEnded():
    global simInProgress 
    simInProgress = False
    return jsonify({
        'message': 'Simulation Over'
        })

def wait_for_user_callback():
    global continueSimulation
    continueSimulation = False
    while not continueSimulation:
        time.sleep(0.1)

@app.route('/simulation-update', methods=['GET'])
def get_simulation_update():
    return jsonify(current_simulation_state)

@app.route('/get-lineup')
def get_lineup():
    team = request.args.get('team')
    players = getPlayers(team)
    return jsonify(players=players)

def getPlayers(team):

    # Make teams
    teamHitters = hitters[hitters['Team'] == team]
    teamHitters = teamHitters[teamHitters['PA'] > 10]
    teamPitchers = pitchers[pitchers['Team'] == team]

    
    return teamHitters['Player'].tolist()
    # return teamHitters

@app.route('/continue', methods=['POST'])
def continue_route():
    global continueSimulation
    continueSimulation = True
    return jsonify({'message': 'Continuing process...'})

if __name__ == '__main__':
    app.run(debug=True)

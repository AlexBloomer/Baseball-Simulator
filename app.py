from flask import Flask, jsonify, request, render_template
from threading import Thread
from Python.Main import run_simulation
from Python.Team import Team
import pandas as pd
import time
app = Flask(__name__)


current_simulation_state = {} # State of sim at a given time. is returned during simulation when sim is fale

continueSimulation = False # Used to wait for the user to press next batter button before continuing 
simInProgress = False # Used to prevent program from starting a new sim if one is already running

# Teams
team1 = None # Away Team
team2 = None # Home TEam

# CSV files
hitters = pd.read_csv('Data/Hitters2024.csv') # Read hitters csv
pitchers = pd.read_csv('Data/Pitchers2024.csv') # Read pitchers csv
hittersPitches = pd.read_csv('Data/HittersPitches2024.csv') # REad hitters pitches csv
pitchersPitches = pd.read_csv('Data/PitchersPitches2024.csv') # Read pitchers pitches csv

#  Route for the root URL
@app.route('/')
def index():
    return render_template('index.html')  # Render HTML page

# Route for starting simulation
@app.route('/run-simulation', methods=['POST'])
def run_simulation_route():
    global team1, team2
    global simInProgress
    global current_simulation_state

    data = request.get_json() # Get input from javascript file

    if not data:
        return jsonify({"error": "Invalid data"}), 400  # Return an error if no data is sent
    
    if simInProgress:
        return jsonify({"error": "simulation already in progress"}), 400 # Return an error if a simulation is already running
    
    # JS input values
    team1Input = data.get('team1')
    team2Input = data.get('team2')
    numSims = int(data.get('numSims'))
    lineup1 = data.get('lineup1')
    lineup2 = data.get('lineup2')

    # Make teams
    team1Hitters = hitters[hitters['Team'] == team1Input]
    team1Hitters = team1Hitters[team1Hitters['PA'] > 0] # Make sure hitters have at least 1 plate appearance
    team2Hitters = hitters[hitters['Team'] == team2Input]
    team2Hitters = team2Hitters[team2Hitters['PA'] > 0] # Make sure hitters have at least 1 plate appearance
    team1Pitchers = pitchers[pitchers['Team'] == team1Input]
    team1Pitchers = team1Pitchers[team1Pitchers['BF'] > 20] # Make sure pitchers have at least 20 batters faced
    team2Pitchers = pitchers[pitchers['Team'] == team2Input]
    team2Pitchers = team2Pitchers[team2Pitchers['BF'] > 20] # Make sure pitchers have at least 20 batters faced
    team1PitchersPitches = pitchersPitches[pitchersPitches['Tm'] == team1Input]
    team1PitchersPitches = team1PitchersPitches[team1PitchersPitches['PA'] > 0] # Make sure hitters have at least 1 plate appearance
    team2PitchersPitches = pitchersPitches[pitchersPitches['Tm'] == team2Input]
    team2PitchersPitches = team2PitchersPitches[team2PitchersPitches['PA'] > 0] # Make sure hitters have at least 1 plate appearance
    team1HittersPitches = hittersPitches[hittersPitches['Tm'] == team1Input]
    team1HittersPitches = team1HittersPitches[team1HittersPitches['PA'] > 0] # Make sure hitters have at least 1 plate appearance
    team2HittersPitches = hittersPitches[hittersPitches['Tm'] == team2Input]
    team2HittersPitches = team2HittersPitches[team2HittersPitches['PA'] > 10] # Make sure pitchers have at least 10 plate appearance
    team1 = Team(team1Input)
    team2 = Team(team2Input)
    team1.fillLineup(team1Hitters, lineup1, team1HittersPitches)
    team2.fillLineup(team2Hitters, lineup2, team2HittersPitches)
    team1.fillPitchingStaff(team1Pitchers, team1PitchersPitches)
    team2.fillPitchingStaff(team2Pitchers, team2PitchersPitches)

    # Set runs and wins to zero for each team
    team1.totalRuns, team2.totalRuns = 0, 0
    team1.wins, team2.wins = 0, 0

    # Call Main.py function run_simulation from thread
    thread = Thread(target=run_simulation, args=(team1, team2, numSims, update_callback, wait_for_user_callback))
    thread.start()

    # thread.join()
    # result = queue.get()
    simInProgress = True
    return jsonify({"message": "Simulation started"}), 200

# Function to update the Javascript file from python data
def update_callback(current_state):
    global current_simulation_state
    current_simulation_state = current_state

# Function called when Javascript finishes simulation
@app.route('/simulation-ended', methods=['POST'])
def simEnded():
    global simInProgress 
    simInProgress = False
    return jsonify({
        'message': 'Simulation Over'
        })

# Function that waits for user to press next batter before continueing code
def wait_for_user_callback():
    global continueSimulation
    continueSimulation = False
    while not continueSimulation:
        time.sleep(0.1)

# Function for updating the Javascript file with information from python file
@app.route('/simulation-update', methods=['GET'])
def get_simulation_update():
    return jsonify(current_simulation_state)

# 
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

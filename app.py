from flask import Flask, jsonify, request, render_template
from threading import Thread
from Python.Main import simulateGames
# from Python.Main import simulateSeason
from Python.DBQueries import get_teams, get_years, get_hitters, get_pitchers, conn, DEFAULT_YEAR
from Python.Team import Team
import pandas as pd
import time

app = Flask(__name__)

current_simulation_state = {}
continueSimulation = False
simInProgress = False

team = None   # Away Team
team2 = None  # Home Team


# Route for the root URL
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game')
def game():
    return render_template('index.html')

@app.route('/season')
def season():
    return render_template('season.html')

# Route for starting simulation
@app.route('/run-simulation', methods=['POST'])
def simulateGamesRoute():
    global team, team2, simInProgress, current_simulation_state

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data"}), 400
    if simInProgress:
        return jsonify({"error": "Simulation already in progress"}), 400

    team1Input = data.get('team1')
    team2Input = data.get('team2')
    numSims    = int(data.get('numSims'))
    lineup1    = data.get('lineup1')
    lineup2    = data.get('lineup2')
    year1       = int(data.get('year1', DEFAULT_YEAR))
    year2       = int(data.get('year2', DEFAULT_YEAR))

    team1Hitters  = get_hitters(team1Input, year1)
    team2Hitters  = get_hitters(team2Input, year2)
    team1Pitchers = get_pitchers(team1Input, year1)
    team2Pitchers = get_pitchers(team2Input, year2)
    team  = Team(team1Input)
    team2 = Team(team2Input)
    team.fillLineup(team1Hitters, lineup1)
    team2.fillLineup(team2Hitters, lineup2)
    team.fillPitchingStaff(team1Pitchers)
    team2.fillPitchingStaff(team2Pitchers)

    team.totalRuns,  team2.totalRuns  = 0, 0
    team.wins,       team2.wins       = 0, 0

    thread = Thread(target=simulateGames, args=(team, team2, numSims, update_callback, wait_for_user_callback))
    thread.start()

    simInProgress = True
    return jsonify({"message": "Simulation started"}), 200

# @app.route('/simulate-season', methods=['POST'])
# def simulateSeasonRoute():
#     global team, simInProgress, current_simulation_state

#     data = request.get_json()
#     if not data:
#         return jsonify({"error": "Invalid data"}), 400
#     if simInProgress:
#         return jsonify({"error": "Simulation already in progress"}), 400

#     teamInput = data.get('team')
#     lineup    = data.get('lineup')
#     numSims   = int(data.get('numSims'))
#     year      = int(data.get('year', DEFAULT_YEAR))

#     teamHitters  = get_hitters(teamInput, year)
#     teamPitchers = get_pitchers(teamInput, year)

#     team = Team(teamInput)
#     team.fillLineup(teamHitters, lineup)
#     team.fillPitchingStaff(teamPitchers)

#     thread = Thread(target=simulateSeason, args=(team, numSims, update_callback, wait_for_user_callback, conn, year))
#     thread.start()

#     simInProgress = True
#     return jsonify({"message": "Simulation started"}), 200

def update_callback(current_state):
    global current_simulation_state
    current_simulation_state = current_state

@app.route('/simulation-ended', methods=['POST'])
def simEnded():
    global simInProgress
    simInProgress = False
    return jsonify({'message': 'Simulation Over'})

@app.route('/simulation-update', methods=['GET'])
def get_simulation_update():
    return jsonify(current_simulation_state)

@app.route('/get-lineup')
def get_lineup():
    teamID = request.args.get('team')
    year   = int(request.args.get('year', DEFAULT_YEAR))
    df = get_hitters(teamID, year)
    players = df.where(pd.notnull(df), None)
    return jsonify(players=players.to_dict(orient="records"))

@app.route('/get-years')
def get_years_route():
    df = get_years()
    return jsonify(years=df['yearID'].tolist())

@app.route('/get-teams', methods=['GET'])
def fill_teams():
    try:
        year = int(request.args.get('year', DEFAULT_YEAR))
        teams = get_teams(year)
        return jsonify(teams=teams)
    except Exception as e:
        print(e)
        return jsonify(error=str(e)), 500

def wait_for_user_callback():
    global continueSimulation
    continueSimulation = False
    while not continueSimulation:
        time.sleep(0.1)

@app.route('/continue', methods=['POST'])
def continue_route():
    global continueSimulation
    continueSimulation = True
    return jsonify({'message': 'Continuing process...'})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=5001)
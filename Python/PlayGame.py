from enum import Enum
import pandas as pd
import random
from Python.PositionPlayer import *
from Python.Bases import Bases
from Python.Team import *
import time

# Game Class
class Game:
    """ Game Constructor
        Args:
            team1: Away Team
            team2: Home Team
            sim: True means it will simulate game immediately, 
                 False means it will run each play and wait for user to press next batter each time
    """
    def __init__(self, team1, team2, sim):
        self.team1 = team1
        self.team2 = team2
        self.bases = Bases()
        self.inning = 1
        self.currentPitcher = None
        self.currentHitter = None
        self.result = None
        self.topInning = True
        self.startTime = time.time()
        self.curTime = time.time()
        self.numGames = 0
        self.resultString = ''
        self.outs = 0
        self.sim = sim

        

    # Update JS with new information
    def getCurrentSimulationState(self):
        #  Update the currentSimState variable with new information
        # print("getting current pitcher")
        currentSimState = {
            'team1_runs': self.team1.runs,
            'team2_runs': self.team2.runs,
            'team1_total_runs': self.team1.totalRuns,
            'team2_total_runs': self.team2.totalRuns,
            'team1_wins': self.team1.wins,
            'team2_wins': self.team2.wins,
            'team1_name': self.team1.name,
            'team2_name': self.team2.name,
            'runners': self.bases.runners,
            'outs': self.outs,
            'inning': self.inning,
            # 'pitcher': self.currentPitcher.__str__(),
            'pitcher': self.team2.getCurrentPitcher().__str__() if self.topInning else self.team1.getCurrentPitcher().__str__(),
            # 'hitter': self.currentHitter.__str__(),
            'hitter': self.team1.getCurrentBatter().__str__() if self.topInning else self.team2.getCurrentBatter().__str__(),
            'onDeckHitter': self.team1.getOnDeckHitter().__str__() if self.topInning else self.team2.getOnDeckHitter().__str__(),
            'result': self.result.value if self.result is not None else "",
            'resultString': self.resultString,
            'gameOver': False,
            'topInning': self.topInning,
            'team1_hitters_names': [hitter.name for hitter in self.team1.lineup],
            'team1_hitters_results': [(hitter.getBoxStats()) for hitter in self.team1.lineup],
            # 'team1_pitchers_names': [pitcher.name for pitcher in self.team1.pitchingStaff],
            # 'team1_pitchers_results': [(pitcher.boxStats) for pitcher in self.team1.pitchingStaff],
            'team2_hitters_names': [hitter.name for hitter in self.team2.lineup],
            'team2_hitters_results': [(hitter.getBoxStats()) for hitter in self.team2.lineup],
            'team1_box_score': self.team1.boxScore,
            'team2_box_score': self.team2.boxScore
        }
        # returns the currentSimState after updating
        return currentSimState

    # Sets the string that will display on screen for each result
    def setResultString(self, hitter, result):
        match result:
            case Result.OUT:
                self.resultString = f'{hitter.name} got out' 
            case Result.WALK:
                self.resultString = f'{hitter.name} walked' 
            case Result.HIT_BY_PITCH:
                self.resultString = f'{hitter.name} was hit by a pitch' 
            case Result.INTENTIONAL_WALK:
                self.resultString = f'{hitter.name} was intentionally walked' 
            case Result.SINGLE:
                self.resultString = f'{hitter.name} singled' 
            case Result.DOUBLE:
                self.resultString = f'{hitter.name} doubled' 
            case Result.TRIPLE:
                self.resultString = f'{hitter.name} tripled' 
            case Result.HOMERUN:
                self.resultString = f'{hitter.name} hit a homerun!!' 
            case Result.SACRIFICE_FLY:
                self.resultString = f'{hitter.name} hit a sacrifice fly' 
            case Result.SACRIFICE_HIT:
                self.resultString = f'{hitter.name} hit a sacrifice bunt' 

    # Returns True if batter got a hit(Single, double, triple, or homerun)
    # Returns False if batter didn't get a hit
    def isHit(self, result):
        return result == Result.SINGLE or result == Result.DOUBLE or result == Result.TRIPLE or result == Result.HOMERUN             

    def playAtBat(self, hittingTeam, pitchingTeam):
        """ Plays one at bat
            Args:
                hittingTeam: the hitting team
                pitchingTeam: the pitching team
            
            Returns:
                The result of the at bat which is a Result enum (ex. Result.SINGLE)
        """
        # hitter and pitcher's stats are weighted equally
        hitterWeight = .5
        pitcherWeight = .5
        # get the current hitter and pitcher
        hitter = hittingTeam.getCurrentBatter()
        pitcher = pitchingTeam.getCurrentPitcher()      

        # Get a random number for the result
        rnd = random.random()
        # Calculate probabilities of each thing happening based on hitter and pitchers stats
        single = hitterWeight * hitter.singlePct + pitcherWeight * pitcher.singlePct
        double = hitterWeight * hitter.doublePct + pitcherWeight * pitcher.doublePct + single
        triple = hitterWeight * hitter.triplePct + pitcherWeight * pitcher.triplePct + double
        homerun = hitterWeight * hitter.homerunPct + pitcherWeight * pitcher.homerunPct + triple
        walk = hitterWeight * hitter.walkPct + pitcherWeight * pitcher.walkPct + homerun
        hbp = hitterWeight * hitter.hbpPct + pitcherWeight * pitcher.hbpPct + walk
        ibb = hitterWeight * hitter.ibbPct + pitcherWeight * pitcher.ibbPct + hbp
        
        # Add a random number of pitches based on the pit/pa of both the hitter and pitcher
        pc = hitterWeight * hitter.pitchPerPA + pitcherWeight * pitcher.pitchPerPA
        if(not self.sim):
            pitcher.addPitches(max(1, round(random.gauss(pc, 1))))
        else:
            pitcher.addPitches(int(pc))
        
        # If a sacrifice is possible add chance for sacrifice based on hitters stats
        if(self.outs < 2 and (self.bases.second() or self.bases.third())):
            sh = hitter.shPct() + ibb
            sf = hitter.sfPct() + sh
        else:
            sh = 0
            sf = 0
        
        # Else if statement to check which result happened based on random number
        # then return result and add runs to both team and players
        if(rnd < single):
            runs =self.bases.hit(hitter.name, 1)
            hittingTeam.runs+=runs
            hitter.addRBI(runs)
            pitcher.addRuns(runs)
            return Result.SINGLE
        
        elif(rnd < double):
            runs = self.bases.hit(hitter.name, 2)
            hitter.addRBI(runs)
            hittingTeam.runs+=runs
            pitcher.addRuns(runs)
            return Result.DOUBLE
        elif(rnd < triple):
            runs = self.bases.hit(hitter.name, 3)
            hitter.addRBI(runs)
            hittingTeam.runs += runs
            pitcher.addRuns(runs)
            return Result.TRIPLE
        elif(rnd < homerun):
            runs = self.bases.advanceBases(4, False, False) + 1
            hitter.addRBI(runs)
            hittingTeam.runs+=runs
            pitcher.addRuns(runs)
            return Result.HOMERUN
        elif(rnd < walk):
            runs=self.bases.walk(hitter.name)
            hitter.addRBI(runs)
            hittingTeam.runs += runs
            pitcher.addRuns(runs)
            return Result.WALK
        elif(rnd < hbp):
            runs=self.bases.walk(hitter.name)
            hitter.addRBI(runs)
            hittingTeam.runs += runs
            pitcher.addRuns(runs)
            return Result.HIT_BY_PITCH
        elif(rnd < ibb):
            runs=self.bases.walk(hitter.name)
            hitter.addRBI(runs)
            hittingTeam.runs += runs
            pitcher.addRuns(runs)
            return Result.INTENTIONAL_WALK
        elif(rnd < sh):
            runs=self.bases.sacrifice()
            hitter.addRBI(runs)
            hittingTeam.runs += runs
            pitcher.addRuns(runs)
            return Result.SACRIFICE_HIT
        elif(rnd < sf):
            runs=self.bases.sacrifice()
            hitter.addRBI(runs)
            hittingTeam.runs += runs
            pitcher.addRuns(runs)
            return Result.SACRIFICE_FLY
        else:
            return Result.OUT

    # Play half of an inning
    def playHalf(self, hittingTeam, pitchingTeam, update_callback, waitForNextBatter):
        runsBefore = hittingTeam.runs
        if(not self.sim):
            update_callback(self.getCurrentSimulationState())
        
        # Keep playing at bats until it gets to three outs
        while self.outs < 3:
            # Check if pitching team should pull the pitcher
            leverage = 0 if abs(hittingTeam.runs - pitchingTeam.runs) > 5 else 1
            leverage = leverage if abs(hittingTeam.runs - pitchingTeam.runs) > 2 else 2
            if(pitchingTeam.curPitcher == None or ( pitchingTeam.shouldPullPitcher(0, self.inning/9))):
                pitchingTeam.setCurrentPitcher(self.inning, self.outs, self.team1.runs-self.team2.runs)
            
            # Play the current at bat
            res = self.playAtBat(hittingTeam, pitchingTeam)
            self.result = res
            hitter = hittingTeam.getCurrentBatter()
            pitcher = pitchingTeam.getCurrentPitcher()
            self.currentHitter = hitter     
            self.currentPitcher = pitcher
            # TODO The next two lines take foreverrrrrrrrrrrrr (About 20 percent of sim time)
            pitcher.addResult(res)
            hitter.addResult(res)

            # If not simming update boxscore for current game
            if not self.sim:
                self.setResultString(hitter, res)
                hittingTeam.boxScore[str(self.inning)] = hittingTeam.runs - runsBefore
                hittingTeam.boxScore['R'] = hittingTeam.runs
                if(self.isHit(res)):
                    hittingTeam.boxScore['H'] += 1
                update_callback(self.getCurrentSimulationState())
            # If player got out
            if(res == Result.OUT or res == Result.SACRIFICE_FLY or res == Result.SACRIFICE_HIT):
                self.outs+=1
                # If three outs break out of loop because inning is over
                if(self.outs ==3):
                    hittingTeam.nextHitter()
                    if(not self.sim):
                        hittingTeam.boxScore[str(self.inning)] = hittingTeam.runs - runsBefore
                        update_callback(self.getCurrentSimulationState())
                        waitForNextBatter()
                    break
            if not self.sim:
                update_callback(self.getCurrentSimulationState())
                waitForNextBatter()
            if(self.inning >=9 and hittingTeam == self.team2 and hittingTeam.runs > pitchingTeam.runs):
                return
            # Set current hitter to be the next hitter
            hittingTeam.nextHitter()
    
    # Play one inning
    def playInning(self, update_callback, waitForNextBatter):
        self.topInning = True
        self.outs = 0
        self.bases.clearBases()
        # Play top half
        self.playHalf(self.team1, self.team2, update_callback, waitForNextBatter)
        
        # If home team is winning and it's the 9th inning or later, end game
        if(self.inning >=9 and self.team1.runs < self.team2.runs):
            return
        self.topInning = False
        self.bases.clearBases()
        self.outs=0
        # Play bottom half
        self.playHalf(self.team2, self.team1, update_callback, waitForNextBatter)

    # Get away team runs
    def getRuns1(self):
        return self.team1.runs
    
    # Get home team runs
    def getRuns2(self):
        return self.team2.runs

    def playGame(self, update_callback, waitForNextBatter):
        """ Play entire game
            Args:
                update_callback: function to update javascript file with information
                waitForNextBatter: function to wait until user clicks nextBatter button
            
            Return: winning team
        """
        self.topInning = True
        self.numGames +=1
        self.startTime = time.time()
        self.team1.newGame()
        self.team2.newGame()
        self.team1.runs = 0
        self.team2.runs = 0
        self.team1.setCurrentPitcher(self.inning, self.outs, self.team1.runs-self.team2.runs)
        self.team2.setCurrentPitcher(self.inning, self.outs, self.team1.runs-self.team2.runs)
        self.currentPitcher = self.team1.getCurrentPitcher()
        self.inning = 1 
        if(not self.sim):
            update_callback(self.getCurrentSimulationState())
            waitForNextBatter()
        
        # Play until they've played 9 innings or until one team is winning after 9 innings
        while(self.inning < 10 or self.team1.runs == self.team2.runs):
            if(not self.sim):
                update_callback(self.getCurrentSimulationState())
            self.playInning(update_callback, waitForNextBatter)
            self.inning+=1
        winner = self.team1 if self.team1.runs > self.team2.runs else self.team2
        if(not self.sim):
            update_callback(self.getCurrentSimulationState())
        return winner

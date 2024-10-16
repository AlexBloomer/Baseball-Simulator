from enum import Enum
import pandas as pd
import random
from Python.PositionPlayer import *
from Python.Bases import Bases
from Python.Team import *
import time

    
class Game:
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
        # self.runs1=None
        # self.runs2=None
        self.outs = 0
        self.sim = sim
    
    def serialize_stats(self, stats):
    # Convert enum keys to strings and keep values unchanged
        return {str(key): value for key, value in stats.items()}

    def getCurrentSimulationState(self):
        current_simulation_state = {
            # 'current_simulation_number':  + 1,
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
            'pitcher': self.currentPitcher.__str__(),
            'hitter': self.currentHitter.__str__(),
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
            # 'team2_pitchers_names': [pitcher.name for pitcher in self.team2.pitchingStaff],
            # 'team2_pitchers_results': [(pitcher.boxStats) for pitcher in self.team2.pitchingStaff],
            # 'team2_hitters_names': self.team2.lineup,
            # 'team2_hitters_results': self.team2.lineup,
            # 'team2_pitchers_names': self.team2.pitchingStaff,
            # 'team2_pitchers_results': self.team2.pitchingStaff

        }
        return current_simulation_state

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
            
        

    def get_weighted_random(self, target, spread):
        # Create a list of numbers around the target with weights
        numbers = list(range(target - spread, target + spread + 1))
        weights = [1/(abs(target - num) + 1) for num in numbers]  # Weights are inversely proportional to distance
        return random.choices(numbers, weights=weights)[0]              

    def playAtBat(self, hittingTeam, pitchingTeam):

        # batter = hittingTeam.curPos
        # time.sleep(7)
        hitterWeight = .5
        pitcherWeight = .5
        hitter = hittingTeam.getCurrentBatter()
        pitcher = pitchingTeam.getCurrentPitcher()      
        # if(not self.sim):
        #     print('\nNEXT HITTER')
        #     print(f"Current Hitter: {hitter}")
        rnd = random.random()
        single = hitterWeight * hitter.singlePct + pitcherWeight * pitcher.singlePct
        double = hitterWeight * hitter.doublePct + pitcherWeight * pitcher.doublePct + single
        triple = hitterWeight * hitter.triplePct + pitcherWeight * pitcher.triplePct + double
        homerun = hitterWeight * hitter.homerunPct + pitcherWeight * pitcher.homerunPct + triple
        walk = hitterWeight * hitter.walkPct + pitcherWeight * pitcher.walkPct + homerun
        hbp = hitterWeight * hitter.hbpPct + pitcherWeight * pitcher.hbpPct + walk
        ibb = hitterWeight * hitter.ibbPct + pitcherWeight * pitcher.ibbPct + hbp
        # double = hitter.doubles/hitter.pa + single
        # triple = hitter.triples/hitter.pa + double
        # hr = hitter.hr/hitter.pa + triple
        # walk = hitter.walks/hitter.pa + hr
        # hbp = hitter.hbp/hitter.pa + walk
        # ibb = hitter.intentionalWalks/hitter.pa + hbp
        # print(f'Chances:\n{single}\n{double}\n{triple}\n{homerun}\n{walk}\n{hbp}\n{ibb}')
        pc = hitterWeight * hitter.pitchPerPA + pitcherWeight * pitcher.pitchPerPA
        # if(pitchCount < rnd):
        # print(pitcher.pitches)
        # rnd = random.random()
        # pitcher.addPitches(4)
        pitcher.addPitches(max(1, round(random.gauss(pc, 1))))
        # print(str(pc))
        # print(str(max(1, round(random.gauss(pc, 1)))))
        if(self.outs < 2 and (self.bases.second() or self.bases.third())):
            sh = hitter.shPct() + ibb
            sf = hitter.sfPct() + sh
        else:
            sh = 0
            sf = 0
        # return Result.SINGLE
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
            
    def playHalf(self, hittingTeam, pitchingTeam, update_callback, wait_for_user_callback):
        # print("Next Half")
        if(not self.sim):
            # print(self.team1.name)
            # print(self.bases)
            # print(f'outs: {self.outs}')
            update_callback(self.getCurrentSimulationState())
        while self.outs < 3:
            leverage = 0 if abs(hittingTeam.runs - pitchingTeam.runs) > 5 else 1
            leverage = leverage if abs(hittingTeam.runs - pitchingTeam.runs) > 2 else 2
            if(pitchingTeam.curPitcher == None or ( pitchingTeam.shouldPullPitcher(leverage, self.inning/9))):
                # print(f'Pitcher Pulled:\nInning: {self.inning}\tOuts:{self.outs}')
                # print('PITCHER PULLED')
                # self.outs = self.outs
                # print(pitchingTeam.getCurrentPitcher())
                pitchingTeam.setCurrentPitcher(self.inning, self.outs, self.team1.runs-self.team2.runs)
                # print(pitchingTeam.getCurrentPitcher())
            
            # res = Result.OUT
            res = self.playAtBat(hittingTeam, pitchingTeam)
            self.result = res
            # if(not self.sim):
                # print(res.value)
            hitter = hittingTeam.getCurrentBatter()
            self.setResultString(hitter, res)
            pitcher = pitchingTeam.getCurrentPitcher()
            self.currentHitter = hitter     
            self.currentPitcher = pitcher
            hitter.addResult(res)
            pitcher.addResult(res)
            if not self.sim:
                update_callback(self.getCurrentSimulationState())
            if(res == Result.OUT or res == Result.SACRIFICE_FLY or res == Result.SACRIFICE_HIT):
                self.outs+=1
                if(self.outs ==3):
                    hittingTeam.nextHitter()
                    if(not self.sim):
                        update_callback(self.getCurrentSimulationState())
                        # print('Score: ')
                        # print(f'{self.team1.name}: {self.team1.runs}')
                        # print(f'{self.team2.name}: {self.team2.runs}')
                        # print('INNING OVER')
                        update_callback(self.getCurrentSimulationState())
                    if(not self.sim):
                        wait_for_user_callback()
                    break
            # self.outs+=1
            if not self.sim:
                # print()
                # print(f'outs: {self.outs}')
                update_callback(self.getCurrentSimulationState())
                # print(self.bases)
                # print('Score: ')
                # print(f'{self.team1.name}: {self.team1.runs}')
                # print(f'{self.team2.name}: {self.team2.runs}')
            if(not self.sim):
                wait_for_user_callback()
            hittingTeam.nextHitter()
    

    def playInning(self, update_callback, wait_for_user_callback):
        # print(f'Inning: {self.inning}')
        # self.curTime = time.time()
        # self.lastTime = self.curTime
        self.topInning = True
        self.outs = 0
        # self.team1.getCurrentPitcher().addInning()
        # self.team2.getCurrentPitcher().addInning()
        self.bases.clearBases()
        # if(not self.sim):
        #     update_callback(self.getCurrentSimulationState())
        self.playHalf(self.team1, self.team2, update_callback, wait_for_user_callback)
        if(self.inning >=9 and self.team1.runs < self.team2.runs):
            return
        self.topInning = False
        self.bases.clearBases()
        self.outs=0
        self.playHalf(self.team2, self.team1, update_callback, wait_for_user_callback)

    def getRuns1(self):
        return self.team1.runs
    def getRuns2(self):
        return self.team2.runs

    def playGame(self, update_callback, wait_for_user_callback):
        self.numGames +=1
        # print(self.numGames)
        self.startTime = time.time()
        if(not self.sim):
            update_callback(self.getCurrentSimulationState())
        self.team1.newGame()
        self.team2.newGame()
        self.team1.runs = 0
        self.team2.runs = 0
        self.inning = 1 
        if(not self.sim):
            wait_for_user_callback()
        # self.team1.setCurrentPitcher(1,0, 0)
        # self.team2.setCurrentPitcher(1,0, 0)
        while(self.inning < 10 or self.team1.runs == self.team2.runs):
            if(not self.sim):
                update_callback(self.getCurrentSimulationState())
            # print(self.inning)
            self.playInning(update_callback, wait_for_user_callback)
            self.inning+=1
        # print(self.team1.curPitcher.pitches)
        # print(self.team2.curPitcher.pitches)
        winner = self.team1 if self.team1.runs > self.team2.runs else self.team2
        if(not self.sim):
            update_callback(self.getCurrentSimulationState())
        return winner

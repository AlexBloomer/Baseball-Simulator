from enum import Enum
from Python.PositionPlayer import Result
class PitcherType(Enum):
    STARTER = "Starter"
    RELIEVER = "Reliever"
    CLOSER = "Closer"
    

class Pitcher:
    def __init__(self, Rk,name,Age,Team,Lg,WAR,W,L,winPct,ERA,G,GS,GF,CG,SHO,SV,IP,H,R,ER,HR,BB,IBB,SO,HBP,BK,WP,BF,ERAPlus,FIP,WHIP,H9,HR9,BB9,SO9,SOperBB,Awards,code, pitchPerPA):
        self.name = name
        self.team = Team
        self.w = W
        self.l = L
        self.era = ERA
        self.g = G
        self.gs = GS
        self.gf = GF
        self.cg = CG
        self.sv = SV
        self.ip = IP
        self.h = H
        self.r = R
        self.er = ER
        self.hr = HR
        self.bb = BB
        self.ibb = IBB
        self.so = SO
        self.hbp = HBP
        self.balks = BK
        self.wildPitches = WP
        self.battersFaced = BF
        self.whip = WHIP
        self.code = code
        self.inningsPerApp = self.ip/self.g
        self.pitchCount = 0
        self.pitchPerPA = pitchPerPA
        # Singles make up 65% of hits
        htemp = self.h - self.hr
        self.singlePct = (htemp*.754)/self.battersFaced
        # self.singlePct = self.h/self.batters
        # doubles make up 19.5% of hits
        self.doublePct = (htemp*.226)/self.battersFaced
        # triples make up 1.75% of hits
        self.triplePct = (htemp*.0203)/self.battersFaced
        # homeruns make up 13.7% of hits
        self.homerunPct = self.hr/self.battersFaced
        self.walkPct = self.bb/self.battersFaced
        self.hbpPct = self.hbp/self.battersFaced
        self.ibbPct = self.ibb/self.battersFaced
        self.pitchType = PitcherType.RELIEVER
        self.setPitchType()
        self.bfSim = 0
        self.abSim = 0
        self.bfSimTotal = 0
        self.abSimTotal = 0
        self.hitsSim = 0
        self.whipSim = 0
        self.ipSim = 0
        self.runSim = 0
        self.pitches = 0
        self.gamesSim = 0
        
        # print(str(self.pitchPerPA))
        results = [Result.SINGLE, Result.DOUBLE, Result.TRIPLE, Result.HOMERUN, Result.WALK, Result.HIT_BY_PITCH, Result.INTENTIONAL_WALK, Result.SACRIFICE_FLY, Result.SACRIFICE_HIT, Result.OUT]
        self.totalStats = dict.fromkeys(results, 0)
        self.gameStats = dict.fromkeys(results, 0)
        results = ['Batters Faced', 'Hits Against', 'Walks Against', 'Batting Average Against Actual', 'Batting Average Against Sim', 'WHIP Actual', 'WHIP Sim',  'ERA Actual', 'ERA Sim']
        self.calcStats = dict.fromkeys(results,0)
    
    def addResult(self, res):
        self.totalStats[res] += 1
        self.gameStats[res] += 1
        self.bfSim+=1

    def getGames(self):
        return self.gamesSim
    
    def addRuns(self, num):
        self.runSim += num
    
    def addInning(self):
        self.ipSim += 1
        
    def getIpSim(self):
        # print(f'IPSim: {(self.gameStats[Result.OUT] + self.gameStats[Result.SACRIFICE_FLY] + self.gameStats[Result.SACRIFICE_HIT])/3}')
        return (self.gameStats[Result.OUT] + self.gameStats[Result.SACRIFICE_FLY] + self.gameStats[Result.SACRIFICE_HIT])/3 
    # def addInning(self):
    #     self.ipSim += 1
    
    def addPitches(self, num):
        self.pitches += num
        self.pitchCount += num
        
    def calculateStats(self):
        if(self.bfSim == 0):
            return
        self.hitsSim += self.totalStats[Result.SINGLE] + self.totalStats[Result.DOUBLE] + self.totalStats[Result.TRIPLE] + self.totalStats[Result.HOMERUN]
        self.abSim = self.hitsSim + self.totalStats[Result.OUT]
        self.basesSim = self.totalStats[Result.SINGLE] + 2*self.totalStats[Result.DOUBLE] + 3*self.totalStats[Result.TRIPLE] + 4*self.totalStats[Result.HOMERUN]
        outs = int(self.ip) * 3
        fi = self.ip-outs
        self.ipSim = (self.totalStats[Result.OUT] + self.totalStats[Result.SACRIFICE_FLY] + self.totalStats[Result.SACRIFICE_HIT])/3
        if fi == 0.1:
            outs += 1
        elif fi == 0.2:
            outs += 2
        abActual = outs + self.h
        # self.ipSim = self.stats[Result.OUT]/3
        # print(self.ipSim)
        self.whipSim = (self.hitsSim + self.totalStats[Result.WALK])/self.ipSim
        self.calcStats['Batters Faced'] = self.bfSim
        self.calcStats['Hits Against'] = self.hitsSim
        self.calcStats['Walks Against'] = self.totalStats[Result.WALK]
        self.calcStats['Batting Average Against Actual'] = self.h/(abActual)
        self.calcStats['Batting Average Against Sim'] = self.hitsSim/self.abSim
        self.calcStats['ERA Actual'] = self.era
        self.calcStats['ERA Sim'] = self.runSim/(self.ipSim/9)
        self.calcStats['Run Sim'] = self.runSim
        self.calcStats['Inning Sim'] = self.ipSim
        self.calcStats['WHIP Sim'] = self.whipSim
        self.calcStats['WHIP Actual'] = self.whip
        
    

    # def getGameResults(self):
    #     maxResult = 16
    #     results = ''
    #     for key, value in self.stats.items():
    #         results += f'{key.value}: {value}\t'
    #     results += '\n\t\t\t\t'
    #     self.calculateStats()
    #     # for key, value in self.calcStats.items():
    #     #     results += f'{key}: {value}\t'
        
    #     return results

    def getGameResults(self):
    # Define the column width for alignment (adjust based on data length)
        col_width = 30  
        results = ''
        
        # Header for the table
        results += f"{f'{self.name}':<{col_width}}{'Stat':<{col_width}}\n"
        results += '-' * (col_width * 2) + '\n'  # Divider line
        
        # Add stats for each pitcher
        for key, value in self.totalStats.items():
            results += f'{key.value:<{col_width}}{value:<{col_width}}\n'
        
        # results += '-' * (col_width * 2) + '\n'  # Divider line
        
        # Add calculated stats
        self.calculateStats()
        for key, value in self.calcStats.items():
            results += f'{key:<{col_width}}{value:<{col_width}}\n'
        
        return results

    def setPitchType(self):
        if(self.g != 0 and self.gs/self.g > 0.5):
            self.pitchType = PitcherType.STARTER
        elif(self.gf != 0 and self.sv/self.gf > 0.5):
            self.pitchType = PitcherType.CLOSER
        else:
            self.pitchType = PitcherType.RELIEVER

    def __str__(self):
        return f"Pitcher: {self.name}<br>Team: {self.team}<br>Pitch Type: {self.pitchType.value}<br>Games: {self.g}<br>ERA: {self.era}<br>Whip:{self.whip}"
    
from enum import Enum

# Postition Enum
class Position(Enum):
    DH = "Designated Hitter"
    CATCHER = "Catcher"
    FIRST_BASE = "First Base"
    SECOND_BASE = "Second Base"
    THIRD_BASE = "Third Base"
    SHORTSTOP = "Shortstop"
    CENTER_FIELD = "Center Field"
    RIGHT_FIELD = "Right Field"
    LEFT_FIELD = "Left Field"

# Result Enum
class Result(Enum):
    SINGLE = "Single"
    DOUBLE = "Double"
    TRIPLE = "Triple"
    HOMERUN = "Homerun"
    WALK = "Walk"
    HIT_BY_PITCH = "Hit By Pitch"
    INTENTIONAL_WALK = "Intentional Walk"
    SACRIFICE_FLY = "Sacrifice Fly"
    SACRIFICE_HIT = "Sacrifice Hit(Bunt)"
    OUT = "Out"


class PositionPlayer:
    def __init__(self, name,team,G,PA,AB,H,doubles,triples,HR,BB,SO,BA,OBP, OPS, SLG, HBP,SH,SF,IBB,Pos,code, pitchPerPA):
        self.name=name
        self.team=team
        self.g = G
        self.pa = PA
        self.ab = AB
        self.hits = H
        self.doubles = doubles
        self.triples = triples
        self.hr = HR
        self.walks = BB
        self.ba = BA
        self.hbp = HBP
        self.obp = OBP
        self.ops = OPS
        self.slg = SLG
        self.sh = SH
        self.sf = SF
        self.intentionalWalks = IBB
        self.posCode = Pos
        self.position = self.getPos()
        self.code = code
        self.singlePct = (self.hits -self.doubles-self.triples-self.hr)/self.pa
        self.doublePct = self.doubles/self.pa
        self.triplePct = self.triples/self.pa
        self.homerunPct = self.hr/self.pa
        self.walkPct = self.walks/self.pa
        self.hbpPct = self.hbp/self.pa
        self.ibbPct = self.intentionalWalks/self.pa 
        self.paSim = 0
        self.abSim = 0
        self.hitsSim = 0
        self.basesSim = 0
        self.rbiSim = 0
        self.runsSim = 0
        self.pitchPerPA = pitchPerPA
        self.boxStatsKeys = ['Name', 'Position', 'AB', 'R', 'H', 'RBI', 'BB', 'K', 'AVG', 'OPS']
        self.boxStats = dict.fromkeys(self.boxStatsKeys,0)
        results = [Result.SINGLE, Result.DOUBLE, Result.TRIPLE, Result.HOMERUN, Result.WALK, Result.HIT_BY_PITCH, Result.INTENTIONAL_WALK, Result.SACRIFICE_FLY, Result.SACRIFICE_HIT, Result.OUT]
        self.stats = dict.fromkeys(results, 0)
        results = ['At Bats', 'Hits', 'Total Bases', 'Batting Average Actual', 'Batting Average Sim', 'OPS Actual', 'OPS Sim', 'SLG Actual', 'SLG Sim', 'OBP Actual', 'OBP Sim']
        self.calcStats = dict.fromkeys(results,0)
    def __str__(self):
        return f"Hitter: {self.name}<br>Position: {self.position.value}<br>Team: {self.team}<br>AVG: {self.ba}<br>OPS: {self.ops}"
    
    def addResult(self, res):
        self.stats[res] += 1
        self.paSim+=1
    
    def addRBI(self, runs):
        self.rbiSim += runs
    
    def addRun(self):
        self.runsSim += 1

    def getBoxStats(self):
        self.boxStats['Name'] = self.name
        self.boxStats['Position'] = self.position.value
        self.boxStats['AB'] = self.abSim
        self.boxStats['R'] = self.runsSim
        self.boxStats['H'] = self.hitsSim
        self.boxStats['RBI'] = self.rbiSim
        self.boxStats['BB'] = self.stats[Result.WALK]
        self.hitsSim = self.stats[Result.SINGLE] + self.stats[Result.DOUBLE] + self.stats[Result.TRIPLE] + self.stats[Result.HOMERUN]
        self.abSim = self.hitsSim + self.stats[Result.OUT]
        avg = self.hitsSim/self.abSim if self.abSim != 0 else 0
        self.boxStats['AVG'] = f"{avg:.3f}"
        self.basesSim = self.stats[Result.SINGLE] + 2*self.stats[Result.DOUBLE] + 3*self.stats[Result.TRIPLE] + 4*self.stats[Result.HOMERUN]
        onBase = self.hitsSim + self.stats[Result.WALK] + self.stats[Result.INTENTIONAL_WALK] + self.stats[Result.HIT_BY_PITCH]
        obp = onBase/(self.paSim-self.stats[Result.SACRIFICE_HIT]) if self.paSim-self.stats[Result.SACRIFICE_HIT] != 0 else 0
        slg = self.basesSim/self.abSim if self.abSim != 0 else 0
        ops = obp + slg
        self.boxStats['OPS'] = f"{ops:.3f}"
        return self.boxStats
    
   
    def calculateStats(self):
        self.hitsSim = self.stats[Result.SINGLE] + self.stats[Result.DOUBLE] + self.stats[Result.TRIPLE] + self.stats[Result.HOMERUN]
        self.abSim = self.hitsSim + self.stats[Result.OUT]
        self.basesSim = self.stats[Result.SINGLE] + 2*self.stats[Result.DOUBLE] + 3*self.stats[Result.TRIPLE] + 4*self.stats[Result.HOMERUN]
        # onBase = self.paSim - self.stats[Result.OUT] - self.stats[Result.SACRIFICE_FLY] - self.stats[Result.SACRIFICE_HIT]
        onBase = self.hitsSim + self.stats[Result.WALK] + self.stats[Result.INTENTIONAL_WALK] + self.stats[Result.HIT_BY_PITCH]
        self.calcStats['Total Bases'] = self.basesSim
        self.calcStats['At Bats'] = self.abSim
        self.calcStats['Hits'] = self.hitsSim
        self.calcStats['Batting Average Sim'] = self.hitsSim/self.abSim
        self.calcStats['SLG Sim'] = self.basesSim/self.abSim
        self.calcStats['OBP Sim'] = onBase/(self.paSim-self.stats[Result.SACRIFICE_HIT])
        self.calcStats['OPS Sim'] = self.calcStats['SLG Sim'] + self.calcStats['OBP Sim']
        self.calcStats['Batting Average Actual'] = self.ba
        self.calcStats['OPS Actual'] = self.ops
        self.calcStats['OBP Actual'] = self.obp
        self.calcStats['SLG Actual'] = self.slg
    

    # def getGameResults(self):
    #     maxResult = 16
    #     results = ''
    #     for key, value in self.stats.items():
    #         results += f'{key.value}: {value}\t'
    #     results += '\n\t\t\t\t'
    #     self.calculateStats()
    #     for key, value in self.calcStats.items():
    #         results += f'{key}: {value}\t'
        
    #     return results
    def getGameResults(self):
    # Define the max column width for alignment
        
        col_width = 30  # Adjust as needed for your longest string
        results = ''
        
        # Display header
        results += f"{f'{self.name}':<{col_width}}{'Stat':<{col_width}}\n"
        results += '-' * (col_width * 2) + '\n'  # Divider line

        # Add stats for each player (using player names as keys)
        for key, value in self.stats.items():
            results += f'{key.value:<{col_width}}{value:<{col_width}}\n'
        
        # results += '-' * (col_width * 2) + '\n'  # Divider line

        # Add calculated stats (from self.calcStats)
        self.calculateStats()  # Ensure stats are calculated
        for key, value in self.calcStats.items():
            results += f'{key:<{col_width}}{value:<{col_width}}\n'
        
        # return 'results'
        return results


    def sfPct(self):
        return self.sf/(self.pa *.11)
    def shPct(self):
        return self.sh/(self.pa *.11)
    
    def getPos(self):
        i=0
        val = self.posCode[i]
        while(val=='*' or val == '/' or val == 'H'):
            val = self.posCode[i]
            i+=1
        match val:
            case 'D':
                return Position.DH
            case '2':
                return Position.CATCHER
            case '3':
                return Position.FIRST_BASE
            case '4':
                return Position.SECOND_BASE
            case '5':
                return Position.THIRD_BASE
            case '6':
                return Position.SHORTSTOP
            case '7':
                return Position.LEFT_FIELD
            case '8':
                return Position.CENTER_FIELD
            case '9':
                return Position.RIGHT_FIELD
            case _:
                print("No position: " + str(val))
                return Position.DH

                

    
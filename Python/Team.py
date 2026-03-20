from Python.PositionPlayer import *
from Python.Pitcher import Pitcher
from Python.Pitcher import PitcherType
import random
import bisect
import math
class Team:
    curPos = 0
    def __init__(self, name, lineup=None, pitchingStaff=None):
        self.name = name
        self.lineup = lineup if lineup is not None else []
        self.pitchingStaff = pitchingStaff if pitchingStaff is not None else []
        self.curPos = 0
        self.runs=0
        self.wins=0
        self.rotation = []
        self.relievers = []
        self.usedToday = []
        self.closer = None
        self.curPitcher = None
        self.starterGames = 0
        self.starterLikelihood = []
        self.relieverGames = 0
        self.relieverLikelihood = []
        self.totalRuns = 0
        self.hits = 0
        self.boxScoreKeys = ['Team', '1','2','3','4','5','6','7','8','9','R','H', 'E']
        self.boxScore = dict.fromkeys(self.boxScoreKeys, 0)
        self.boxScore['Team'] = self.name
        self.pitchSetup()
        self.nextPitcher = None
        self.curPitcherId = -1
        self.cumulative_weights = None
        self.numStarters = 0

    def fillLineup(self, team, lineup):
        team = team.fillna(0)
        i = 0
        for name in lineup:
            for index, row in team.iterrows():
                if row['Player'] == name:
                    pa = row['AB'] + row['BB'] + row.get('HBP', 0) + row.get('SF', 0) + row.get('SH', 0)
                    pa = pa if pa > 0 else row['AB']
                    ba = row['H'] / row['AB'] if row['AB'] > 0 else 0
                    obp = round((row['H'] + row['BB']) / pa if pa > 0 else 0,3)
                    slg = round((row['H'] + row['H2B'] + 2*row['H3B'] + 3*row['HR']) / row['AB'] if row['AB'] > 0 else 0,3)
                    ops = float(f"{(obp+slg):.3f}")
                    self.addHitter(PositionPlayer(
                        row['Player'], row['Team'], row['G'], pa,
                        row['AB'], row['H'], row['H2B'], row['H3B'], row['HR'],
                        row['BB'], row['SO'], row['BA'], obp, ops, slg,
                        row.get('HBP', 0), row.get('SH', 0), row.get('SF', 0),
                        row.get('IBB', 0), row.get('POS'), 
                        row['playerID'], 4       # No pitchPerPA, default to 4
                    ))
            if i == 8:
                break
            i += 1
    
    def fillLineupTest(self, team):
        i = 0
        for index, row in team.iterrows():
            pa = row['AB'] + row['BB'] + row.get('HBP', 0) + row.get('SF', 0) + row.get('SH', 0)
            pa = pa if pa > 0 else row['AB']
            obp = (row['H'] + row['BB']) / pa if pa > 0 else 0
            slg = (row['H'] + row['H2B'] + 2*row['H3B'] + 3*row['HR']) / row['AB'] if row['AB'] > 0 else 0
            self.addHitter(PositionPlayer(
                row['Player'], row['Team'], row['G'], pa,
                row['AB'], row['H'], row['H2B'], row['H3B'], row['HR'],
                row['BB'], row['SO'], row['BA'], obp, obp+slg, slg,
                row.get('HBP', 0), row.get('SH', 0), row.get('SF', 0),
                row.get('IBB', 0), 'D', row['playerID'], 4
            ))
            if i == 8:
                break
            i += 1
    def fillPitchingStaff(self, pitchingStaff):
        pitchingStaff = pitchingStaff.fillna(0)
        for index, row in pitchingStaff.iterrows():
            if row['G'] > 10:
                ip = row['IPouts'] / 3
                whip = (row['H'] + row['BB']) / ip if ip > 0 else 0
                bf = row.get('BF', row['IPouts'])  # BFP in our DB
                self.addPitcher(Pitcher(
                    0,                        # Rk
                    row['Player'],
                    0,                        # Age
                    row['Team'], row['lgID'],
                    0,                        # WAR
                    row['W'], row['L'],
                    row['W']/row['G'] if row['G'] > 0 else 0,  # W-L%
                    row['ERA'], row['G'], row['GS'], row['GF'],
                    row['CG'], row['SHO'], row['SV'],
                    ip,
                    row['H'], row['R'], row['ER'], row['HR'],
                    row['BB'], row.get('IBB', 0), row['SO'],
                    row.get('HBP', 0), row.get('BK', 0), row.get('WP', 0),
                    bf,
                    0,        # ERA+
                    0,        # FIP
                    whip,
                    0, 0, 0, 0, 0,  # H9, HR9, BB9, SO9, SO/BB
                    '',             # Awards
                    row['playerID'],
                    4               # pitchPerPA default
            ))
        self.pitchSetup()
    def addHitter(self, player):
        self.lineup.append(player)
    
    def addPitcher(self, player):
        self.pitchingStaff.append(player)
        if(player.pitchType == PitcherType.STARTER):
            self.rotation.append(player)
        elif player.pitchType == PitcherType.RELIEVER:
            self.relievers.append(player)
        else:
            self.closer = player

    
    def weighted_choice(self, elements, weights):
        rnd = random.random() * weights[-1]
        index = bisect.bisect_right(weights, rnd)
        return elements[index]
        
    def newGame(self):
        self.curPitcher = None
        for pitcher in self.pitchingStaff:
            pitcher.pitchCount = 0
            pitcher.runSim = 0
            pitcher.gameStats = {key:0 for key in pitcher.gameStats}
    
    def pitchSetup(self):
        for pitcher in self.rotation:
            self.starterGames += pitcher.g
        for pitcher in self.rotation:
            self.starterLikelihood.append(pitcher.g/self.starterGames)
        for pitcher in self.relievers:
            self.relieverGames += pitcher.g
        for pitcher in self.relievers:
            self.relieverLikelihood.append(pitcher.g/self.relieverGames)
        self.starterWeights = [sum(self.starterLikelihood[:i+1]) for i in range(len(self.starterLikelihood))]
        self.relieverWeights = [sum(self.relieverLikelihood[:i+1]) for i in range(len(self.relieverLikelihood))]

    def setCurrentPitcher(self, inning, outs, scoreDif):
        if(inning == 1 and outs == 0 or self.curPitcher == None):
            self.curPitcher = self.weighted_choice(self.rotation, self.starterWeights)
            self.curPitcher.gamesSim += 1
            self.numStarters += 1
        elif(inning < 9 or abs(scoreDif) > 3 or self.curPitcher.pitchType == PitcherType.CLOSER) or not self.closer:
            if(len(self.relieverWeights) != 0):
                self.curPitcher = self.weighted_choice(self.relievers, self.relieverWeights)
                self.curPitcher.gamesSim +=1
        else:
            self.curPitcher = self.closer
            self.curPitcher.gamesSim +=1
    
    def getCurrentPitcher(self):
        return self.curPitcher
        
    def nextHitter(self):
        self.curPos = (self.curPos+1) if self.curPos<8 else 0
        
    def getOnDeckHitter(self):
        return self.lineup[(self.curPos+1) if self.curPos<8 else 0]

    def getCurrentBatter(self):
        return self.lineup[self.curPos]
    
    def getLineup(self):
        lineupString = f'{self.name} Hitters:\n'
        for player in self.lineup:
            lineupString += str(player) + "\n"
        return lineupString
    
    def getRotation(self):
        rotationString = f'{self.name} Pitchers:\nSTARTERS:\n'
        for player in self.rotation:
            rotationString += str(player) + "\n"
        rotationString += f'RELIEVERS:\n'
        for player in self.relievers:
            rotationString += str(player) + "\n"
        rotationString += f'CLOSER:\n{self.closer}\n'
        return rotationString
    
    def shouldPullPitcher(self, leverage, scale):
        # return False
        maxPitchesStarter = 125
        maxPitchesReliever = 50
        pitchCount = self.curPitcher.pitchCount
        runSim = self.curPitcher.runSim
        ipSim = self.curPitcher.getIpSim()
        removal_prob = 0
        match self.curPitcher.pitchType:
            case PitcherType.STARTER:
                removalProbability = (scale * pitchCount/maxPitchesStarter * .3 
                                      + scale * 0.1*runSim 
                                      + 0.1*ipSim * scale) ** 4
            case PitcherType.RELIEVER:
                removalProbability = (pitchCount/maxPitchesReliever*.5 
                                      + 0.2*runSim
                                      + .0125 * leverage) ** 2
                if(scale == 1):
                    removalProbability *= 2
            case PitcherType.CLOSER:
                removalProbability = (pitchCount/maxPitchesReliever*.5 
                                      + 0.3*runSim 
                                      + 0.025*leverage) ** 4
        removal_prob = min(1.0, removal_prob)

        # Adjust probability if it's low
        if removal_prob < 0.25:
            removal_prob /= 10
        return random.random() < removalProbability


    


    
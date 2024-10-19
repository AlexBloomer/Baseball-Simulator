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

    def fillLineup(self, team, lineup, hitterPitches):
        i=0
        for name in lineup:
            for index, row in team.iterrows():
                filtered = hitterPitches[hitterPitches['Name-additional'] == row['Player-additional']]
                if row['Player'] == name:
                    if not filtered.empty:
                        pitchPerPA = filtered['Pit/PA'].values[0]
                    else:
                        print(f"No matching hitter found for {row['Player-additional']}.")
                        continue

                    self.addHitter(PositionPlayer(row['Player'], row['Team'], row['G'], row['PA'],row['AB'],row['H'],row['2B'],row['3B'],row['HR'],row['BB'],row['SO'],row['BA'],row['OBP'],row['OPS'], row['SLG'], row['HBP'],row['SH'],row['SF'],row['IBB'],row['Pos'],row['Player-additional'], pitchPerPA))
            if(i==8):
                break
            else:
                i+=1

    def fillPitchingStaff(self, pitchingStaff, hitterPitches):
        i=0
        for index, row in pitchingStaff.iterrows():
            if(row['G'] > 10):
                filtered = hitterPitches[hitterPitches['Name-additional'] == row['Player-additional']]
                # pitchPerPA = hitterPitches[hitterPitches['Name-additional'] == row['Player-additional']]['Pit/PA'].values[0]
                # filtered = hitterPitches[hitterPitches['Name-additional'] == row['Player-additional']]
                if not filtered.empty:
                    pitchPerPA = filtered['Pit/PA'].values[0]
                else:
                    pitchPerPA = 5
                    print(f"No matching pitcher found for {row['Player-additional']}.")
                    continue
                self.addPitcher(Pitcher(row['Rk'],row['Player'],row['Age'],row['Team'],row['Lg'],['WAR'],row['W'],row['L'],row['W-L%'],row['ERA'],row['G'],row['GS'],row['GF'],row['CG'],row['SHO'],row['SV'],row['IP'],row['H'],row['R'],row['ER'],row['HR'],row['BB'],row['IBB'],row['SO'],row['HBP'],row['BK'],row['WP'],row['BF'],row['ERA+'],row['FIP'],row['WHIP'],row['H9'],row['HR9'],row['BB9'],row['SO9'],row['SO/BB'],row['Awards'],row['Player-additional'], pitchPerPA))
        i = 0
        for pitcher in self.pitchingStaff:
            if pitcher.pitchType == PitcherType.STARTER:
                self.rotation.append(pitcher)
            elif pitcher.pitchType == PitcherType.RELIEVER and pitcher.g > 15:
                self.relievers.append(pitcher)
            else:
                self.closer = pitcher
        self.pitchSetup()
        self.nextPitcher = self.rotation[0]

    def addHitter(self, player):
        self.lineup.append(player)
    
    def addPitcher(self, player):
        self.pitchingStaff.append(player)
    
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
        elif(inning < 9 or abs(scoreDif) > 3 or self.curPitcher.pitchType == PitcherType.CLOSER):
            self.curPitcher = self.weighted_choice(self.relievers, self.relieverWeights)
            self.curPitcher.gamesSim +=1
        else:
            self.curPitcher = self.closer
            self.curPitcher.gamesSim +=1
        # print(self.curPitcher)
    
    def getCurrentPitcher(self):
        # print(self.curPitcher)
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


    


    
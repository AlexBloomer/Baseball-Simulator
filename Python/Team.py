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
        self.pitchSetup()
        self.nextPitcher = None
        self.curPitcherId = -1
        self.cumulative_weights = None
        self.numStarters = 0

    def fillLineup(self, team, lineup, hitterPitches):
        i=0
        # print(lineup)
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
        # print(self.getLineup())

    def fillPitchingStaff(self, pitchingStaff, hitterPitches):
        i=0
        for index, row in pitchingStaff.iterrows():
            if(row['G'] > 18):
                filtered = hitterPitches[hitterPitches['Name-additional'] == row['Player-additional']]
                # pitchPerPA = hitterPitches[hitterPitches['Name-additional'] == row['Player-additional']]['Pit/PA'].values[0]
                # filtered = hitterPitches[hitterPitches['Name-additional'] == row['Player-additional']]
                if not filtered.empty:
                    # print(filtered['Pit/PA'].values[0])
                    pitchPerPA = filtered['Pit/PA'].values[0]
                else:
                    pitchPerPA = 5
                    # print(row['Player'])
                    print(f"No matching pitcher found for {row['Player-additional']}.")
                    continue
                self.addPitcher(Pitcher(row['Rk'],row['Player'],row['Age'],row['Team'],row['Lg'],['WAR'],row['W'],row['L'],row['W-L%'],row['ERA'],row['G'],row['GS'],row['GF'],row['CG'],row['SHO'],row['SV'],row['IP'],row['H'],row['R'],row['ER'],row['HR'],row['BB'],row['IBB'],row['SO'],row['HBP'],row['BK'],row['WP'],row['BF'],row['ERA+'],row['FIP'],row['WHIP'],row['H9'],row['HR9'],row['BB9'],row['SO9'],row['SO/BB'],row['Awards'],row['Player-additional'], pitchPerPA))
        for pitcher in self.pitchingStaff:
            if pitcher.pitchType == PitcherType.STARTER:
                self.rotation.append(pitcher)
            elif pitcher.pitchType == PitcherType.RELIEVER and pitcher.g > 22:
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
        # print()
        # self.curPitcher =  self.rotation[0]
        # return
        if(inning == 1 and outs == 0):
            # self.curPitcher = self.nextPitcher
            # self.curPitcherId += self.rotation.index(self.curPitcher)
            # self.nextPitcher = self.rotation[self.curPitcherId + 1] if self.curPitcherId < len(self.rotation) else self.rotation[0]
            # self.curPitcher = random.choices(self.rotation, weights=self.starterLikelihood)[0]
            self.curPitcher = self.weighted_choice(self.rotation, self.starterWeights)
            self.curPitcher.gamesSim += 1
            self.numStarters += 1
            # print(f'Setting starter {self.numStarters}')
        elif(inning < 9 or abs(scoreDif) > 3 or self.curPitcher.pitchType == PitcherType.CLOSER):
            self.curPitcher = self.weighted_choice(self.relievers, self.relieverWeights)
            self.curPitcher.gamesSim +=1
            # self.curPitcher = random.choice(self.relievers)
            # temp = random.choices(self.relievers, weights=self.relieverLikelihood, k=1)[0]
            # while(temp == self.curPitcher):
            #     temp = random.choices(self.relievers, weights=self.relieverLikelihood, k=1)[0]
            # self.curPitcher = temp
            # if self.curPitcher in self.relievers:
            #     # Temporarily set the current pitcher's weight to 0
            #     weights = self.relieverLikelihood[:]
            #     cur_index = self.relievers.index(self.curPitcher)
            #     weights[cur_index] = 0

            #     # Choose a new reliever based on adjusted weights
            #     self.curPitcher = random.choices(self.relievers, weights=weights, k=1)[0]
            # else:
            #     # If the current pitcher isn't in relievers, just pick a new one
            #     self.curPitcher = random.choices(self.relievers, weights=self.relieverLikelihood, k=1)[0]
            # self.curPitcher = random.choices(self.relievers, weights=self.relieverLikelihood, k=1)[0]
        else:
            self.curPitcher = self.closer
            self.curPitcher.gamesSim +=1

        # self.curPitcher = self.rotation[1]
    
    def getCurrentPitcher(self):
        return self.curPitcher
        
    def nextHitter(self):
        self.curPos = (self.curPos+1) if self.curPos<8 else 0
        
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
        # return True
        maxPitches = 125
        # print(f'Pitches: {self.curPitcher.pitchCount}\t scale: {scale}\truns: {self.curPitcher.runSim}\t innings: {self.curPitcher.getIpSim()}')
        match self.curPitcher.pitchType:
            case PitcherType.STARTER:
                removalProbability = (scale * self.curPitcher.pitchCount/maxPitches * .3 + scale * 0.1*self.curPitcher.runSim + 0.1*self.curPitcher.getIpSim() * scale) ** 4
                removalProbability = min(1.0, removalProbability)
                if(removalProbability < .25):
                    removalProbability /= 10
                return random.random() < removalProbability
            case PitcherType.RELIEVER:
                maxPitches = 50
                removalProbability = (self.curPitcher.pitchCount/maxPitches*.5 + 0.2*self.curPitcher.runSim) ** 2
                removalProbability = min(1.0, removalProbability)
                if(scale == 1):
                    removalProbability *= 2
                if(removalProbability < .25):
                    removalProbability /= 10
                return random.random() < removalProbability
            case PitcherType.CLOSER:
                maxPitches = 50
                removalProbability = (self.curPitcher.pitchCount/maxPitches*.5 + 0.3*self.curPitcher.runSim + 0.025*leverage) ** 4
                removalProbability = min(1.0, removalProbability)
                return random.random() < removalProbability
                

    def getHitterResults(self):
        # maxName = max(len(player.name) for player in self.lineup)
        resultString = ''
        resultString += f'{self.rotation[1].getGameResults()}\n'
        # for player in self.relievers:
        #     # resultString += f'{player.name}({player.paSim})\n {player.getGameResults()}\n'
        #     resultString += f'{player.getGameResults()}\n'
        # for player in self.lineup:
        #     # resultString += f'{player.name}({player.paSim})\n {player.getGameResults()}\n'
        #     resultString += f'{player.getGameResults()}\n'
        # for player in self.rotation:
            # resultString += f'{player.name}({player.paSim})\n {player.getGameResults()}\n'
            # resultString += f'{player.getGameResults()}\n'
        #     # resultString = resultString.replace('\t', '    ')
        # resultString += f'{self.closer.getGameResults()}\n'
        return resultString
        # return resultString


    


    
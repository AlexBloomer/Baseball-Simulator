import random
class Bases:
    def __init__(self):
        self.runners = {}  # Use a dictionary to store runners

    def clearBases(self):
        self.runners.clear()  # Clear all runners

    def hit(self, name, base):
        runs = self.advanceBases(base, False, False)
        self.runners[name] = base  # Add a runner with an ID
        return runs
    
    def walk(self, name):
        runs = self.advanceBases(1, True, False)
        self.runners[name] = 1  # Add a runner with an ID
        return runs
    
    def sacrifice(self):
        runs = self.advanceBases(1, False, True)
        return runs
    
    def first(self):
        return 1 in self.runners.values()
    
    def second(self):
        return 2 in self.runners.values()
    
    def third(self):
        return 3 in self.runners.values()
    
    def prevFull(self, runner):
        val = self.runners[runner]
        match val:
            case 1:
                return True
            case 2:
                return self.first()
            case 3:
                return self.first() and self.second()

    def advanceBases(self, numBases, walk, sac):
        score = 0
        runners_to_remove = []

        # Advance each runner
        firstToThird = .25
        for name in list(self.runners.keys()):  # Iterate through the keys
            new_position = self.runners[name] + numBases
            if(not walk):
                rnd = random.random()
                match self.runners[name]:
                    case 1:
                        if(numBases==1 and not sac and not self.third()):
                            if(rnd < firstToThird):
                                new_position += 1
                        elif(numBases==2 and not sac):
                            if(rnd < .5):
                                new_position += 1
                                break
                    case 2:
                        if(numBases==1 and not sac):
                            if(rnd < .65):
                                new_position += 1
                                if(self.first()):
                                    firstToThird = .9
                                    

                        
            if(walk and not self.prevFull(name)):
                continue
            # Check if the runner has scored
            if new_position >= 4:
                score += 1
                runners_to_remove.append(name)  # Mark for removal
            else:
                self.runners[name] = new_position  # Update runner's position

        # Remove runners who have scored
        for name in runners_to_remove:
            del self.runners[name]

        return score

    def __str__(self):
        return f"Runners on bases: {self.runners}"
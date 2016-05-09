import logging
import random

import sys

import game
from bfsSearch import ReinforcementSearch
from game import Directions

class AbstractQState():

    def __init__(self, state, direction, name, intersections):
        #self.state = state
        self.intersections = intersections
        # TODO: check this => these keys are not in featue but in stateSearch/ searchResult
        features = RuleGenerator().getStateSearch(state,direction, name, intersections)
        self.ghostThreat = features['nearestGhostDistances']
        self.foodDistance = features['nearestFoodDist']
        self.powerPelletDist = features['nearestPowerPelletDist']
        self.intersections = features['intersections']
        # self.eatableGhosts = features['nearestEatableGhostDistances']
        #self.direction = direction

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            # return self.ghostThreat == other.ghostThreat and self.foodDistance == other.foodDistance and self.powerPelletDist == other.powerPelletDist and self.eatableGhosts == other.eatableGhosts
            return self.ghostThreat == other.ghostThreat and self.foodDistance == other.foodDistance and self.powerPelletDist == other.powerPelletDist #and self.instersections == other.intersections
        else:
            return False
    def __hash__(self):
        # return hash(hash(self.ghostThreat) + hash(self.foodDistance) + hash(self.powerPelletDist) + hash(self.eatableGhosts))
        return hash(hash(self.ghostThreat) + hash(self.foodDistance) + hash(self.powerPelletDist) + hash(self.intersections))

class Saving():
    def __init__(self, evalFn="scoreEvaluation", name=None):
        self.savedStates = {}
        self.name = name

    def getRatingForNextState(self, direction, state, intersection):
        abstractState = AbstractQState(state, direction, self.name, intersection)
        value = self.savedStates.get(abstractState)
        if value == None:
            return 0
        else:
            return value

    def setRatingForState(self, direction, state, value, intersections):
        abstractState = AbstractQState(state, direction, self.name, intersections)
        self.savedStates[abstractState] = value

    def getBestDirection(self, state, directions, intersection):
        bestVal = float('-inf')
        bestDirection = None
        for direction in directions:
            tmpValue = self.getRatingForNextState(direction, state, intersection)
            if bestVal < tmpValue:
                bestVal = tmpValue
                bestDirection = direction
        return bestDirection

    def getBestValue(self, state, directions, intersections):
        bestDirection = self.getBestDirection(state,directions, intersections)
        if bestDirection:
            return self.getRatingForNextState(bestDirection, state, intersections)
        else:
            return 0.0

    def __repr__(self):
        return str(self.savedStates)

class ReinforcementQAgent(game.Agent):
    def __init__(self, numTraining = 0):
         self.name = "qAgent"
         self.intersections = []
         self.saving = Saving(self.name)
         self.random = random.Random()
         self.lastState = None
         self.lastAction = None
         self.alpha = 0.1
         self.gamma = 0.5
         self.epsilon = 0.2
         self.numTraining = int(numTraining)
         self.episodesSoFar = 0

    def getAction(self, state):
        logging.debug(str(state))
        self.lastAction = self.chooseAction(state)
        #print "qAgent called."
        return self.lastAction

    def chooseAction(self, state):
        directions = self.legaldirections(state)
        rnd = self.random.random()
        if self.epsilon > rnd:
            logging.debug("random " + str(rnd) + " gamma " + str(self.epsilon))
            #print "chooseAction: random"
            return self.random.choice(directions)
        else:
            #print "chooseAction: " + self.saving.getBestDirection(self.lastState, directions)
            return self.saving.getBestDirection(self.lastState, directions, self.intersections)

    def calcReward(self, state):
        return state.getScore() - self.lastState.getScore()

    def legaldirections(self, state):
        directions = state.getLegalPacmanActions()
        self.safeListRemove(directions, Directions.LEFT)
        self.safeListRemove(directions, Directions.REVERSE)
        self.safeListRemove(directions, Directions.RIGHT)
        #self.safeListRemove(directions, Directions.STOP)
        return directions

    def safeListRemove(self,lst,item):
        try:
            lst.remove(item)
        except ValueError:
            pass

    def updater(self, state):
        reward = self.calcReward(state)
        currentValue = self.saving.getRatingForNextState(self.lastAction, self.lastState)
        maxPossibleFutureValue = self.saving.getBestValue(state, self.legaldirections(state))
        calcVal =  currentValue + self.alpha * (reward + self.gamma * maxPossibleFutureValue - currentValue)
        self.saving.setRatingForState(self.lastAction, self.lastState, calcVal)
        #self.printQ(state, currentValue, maxPossibleFutureValue, calcVal, self.lastAction)

    def observationFunction(self, state, intersections):
        if self.lastState:
            self.updater(state)
        self.lastState = state
        return state

    def final(self, state):
        self.updater(state)
        self.lastState = None
        self.lastAction = None
        if self.isInTraining():
            self.episodesSoFar += 1
            logging.info("Training " + str(self.episodesSoFar) + " of " + str(self.numTraining))
        else:
            self.epsilon = 0.0
            self.alpha = 0.0

    def isInTraining(self):
        return self.episodesSoFar < self.numTraining

    def isInTesting(self):
        return not self.isInTraining()

    def printQ(self, state, currentValue, maxPossibleFutureValue, calcVal, lastAction):
        print "\nlast State Score " + str(self.lastState.getScore())
        print "new Score :" + str(state.getScore())
        print "last Action : " + str(lastAction)
        print "currentValue: " + str(currentValue) + " MaxPossibleFutureVal: " + str(maxPossibleFutureValue)
        print "calcValue : " + str(calcVal)

class ReinforcementQEAgent(game.Agent):
    def __init__(self, numTraining = 0):
         self.name = "qEAgent"
         self.intersections = []
         self.saving = Saving()
         self.random = random.Random()
         self.lastState = None
         self.lastAction = None
         self.alpha = 0.1
         self.gamma = 0.5
         self.epsilon = 0.2
         self.numTraining = int(numTraining)
         self.episodesSoFar = 0

    def getAction(self, state):
        logging.debug(str(state))
        self.lastAction = self.chooseAction(state)
        #print "qAgent called."
        return self.lastAction

    def chooseAction(self, state):
        directions = self.legaldirections(state)
        rnd = self.random.random()
        if self.epsilon > rnd:
            logging.debug("random " + str(rnd) + " gamma " + str(self.epsilon))
            #print "chooseAction: random"
            return self.random.choice(directions)
        else:
            #print "chooseAction: " + self.saving.getBestDirection(self.lastState, directions)
            return self.saving.getBestDirection(self.lastState, directions, self.intersections)

    def calcReward(self, state):
        return state.getScore() - self.lastState.getScore()

    def legaldirections(self, state):
        directions = state.getLegalPacmanActions()
        self.safeListRemove(directions, Directions.LEFT)
        self.safeListRemove(directions, Directions.REVERSE)
        self.safeListRemove(directions, Directions.RIGHT)
        #self.safeListRemove(directions, Directions.STOP)
        return directions

    def safeListRemove(self,lst,item):
        try:
            lst.remove(item)
        except ValueError:
            pass

    def updater(self, state):
        print " ------------- updater called ------------- "
        reward = self.calcReward(state) # reward = score, not Q-learning reward
        currentValue = self.saving.getRatingForNextState(self.lastAction, self.lastState, self.intersections)
        maxPossibleFutureValue = self.saving.getBestValue(state, self.legaldirections(state), self.intersections)
        calcVal =  currentValue + self.alpha * (reward + self.gamma * maxPossibleFutureValue - currentValue)
        self.saving.setRatingForState(self.lastAction, self.lastState, calcVal, self.intersections)
        #self.printQ(state, currentValue, maxPossibleFutureValue, calcVal, self.lastAction)

    def observationFunction(self, state, intersections):
        if self.lastState:
            self.intersections = intersections
            self.updater(state)
        self.lastState = state
        return state

    def final(self, state):
        self.updater(state)
        self.lastState = None
        self.lastAction = None
        if self.isInTraining():
            self.episodesSoFar += 1
            logging.info("Training " + str(self.episodesSoFar) + " of " + str(self.numTraining))
        else:
            self.epsilon = 0.0
            self.alpha = 0.0

    def isInTraining(self):
        return self.episodesSoFar < self.numTraining

    def isInTesting(self):
        return not self.isInTraining()

    def printQ(self, state, currentValue, maxPossibleFutureValue, calcVal, lastAction):
        print "\nlast State Score " + str(self.lastState.getScore())
        print "new Score :" + str(state.getScore())
        print "last Action : " + str(lastAction)
        print "currentValue: " + str(currentValue) + " MaxPossibleFutureVal: " + str(maxPossibleFutureValue)
        print "calcValue : " + str(calcVal)


class myDict(dict):
    def __init__(self, default):
        self.default = default

    def __getitem__(self, key):
        self.setdefault(key, self.default)
        return dict.__getitem__(self, key)

    def sumAll(self):
        sumAllret = 0.0
        for key in self.keys():
            sumAllret += self[key]
        return sumAllret

    def normalize(self):
        sumAlla = self.sumAll()
        if sumAlla == 0.0:
            newValue = float(1)/len(self)
            for key in self.keys():
                self[key] = newValue
        else:
            for key in self.keys():
                self[key] = self[key] / sumAlla

    def divideAll(self, value):
        for key in self.keys():
            self[key] = float(self[key]) / value

class RuleGenerator():
    def directionToCoordinate(self, direction):
        if direction == Directions.NORTH:
            return (0,1)
        elif direction == Directions.SOUTH:
            return (0,-1)
        elif direction == Directions.EAST:
            return (1,0)
        elif direction == Directions.WEST:
            return (-1,0)
        else:
            return (0,0)
    def getMovableDirections(self,posX,posY, walls):
        lst = [(0,0)]
        try:
            if not walls[posX][posY+1]:
                lst.append((posX, posY+1))
        except IndexError:
            pass

        try:
            if not walls[posX][posY-1]:
                lst.append((posX, posY-1))
        except IndexError:
            pass

        try:
            if not walls[posX-1][posY]:
                lst.append((posX-1, posY))
        except IndexError:
            pass

        try:
            if not walls[posX+1][posY]:
                lst.append((posX+1, posY))
        except IndexError:
            pass

        return lst


    def abstractBroadSearch(self,field, startingPosition, stopCondition):
        startX, startY = startingPosition
        openList = [(startX, startY, 0)]
        closedList = set()
        while openList:
            curX, curY, dist = openList.pop(0)
            if not (curX, curY) in closedList:
                closedList.add((curX, curY))
                if stopCondition(curX, curY):
                    return [dist,(curX, curY)]
                for (sucX, sucY) in self.getMovableDirections(curX, curY,field):
                    openList.append((sucX, sucY, dist + 1))
        return [None,None]

    def abstractBroadSearch2(self,field, startingPosition, x,y):
        startX, startY = startingPosition
        openList = [(startX, startY, 0)]
        closedList = set()
        while openList:
            curX, curY, dist = openList.pop(0)
            if not (curX, curY) in closedList:
                closedList.add((curX, curY))
                if curX == x and curY == y:
                    return [dist,(curX, curY)]
                for (sucX, sucY) in self.getMovableDirections(curX, curY,field):
                    openList.append((sucX, sucY, dist + 1))
        return [None,None]

    def getNearestFoodPosition(self,state, pacmanSpositionAfterMoving):
        food = state.getFood()
        nonEatableGhosts = self.getNonEatableGhosts(state)
        def stopCondition(curX,curY):
            #print "########## foood stopCond. " + str(food[curX][curY] and not (curX,curY) in nonEatableGhosts)
            #print "curX="+str(food[curX])+" curY="+str(food[curY])
            #print "food::: " + str(food)
            return food[curX][curY] and not (curX, curY) in nonEatableGhosts
        return self.abstractBroadSearch(state.getWalls(), pacmanSpositionAfterMoving, stopCondition)[0]

    def getIntersectionDistances(self, state, pacmanSpositionAfterMoving, intersections):
        nonEatableGhosts = self.getNonEatableGhosts(state)
        closestIntersection = intersections[0][0]
        closest = None
        closestIntX = None
        closestIntY = None
        for item in intersections:
            tmpDis = self.abstractBroadSearch2(state.getWalls(), pacmanSpositionAfterMoving , item[0],item[1])[0]
            if (closest == None):
                closest = tmpDis
            if (tmpDis<closest):
                closest = tmpDis
                closestIntersection = self.abstractBroadSearch2(state.getWalls(), pacmanSpositionAfterMoving , item[0], item[1])[1]
                closestIntX = item[0]
                closestIntY = item[1]

        if(closestIntX == None or closestIntY == None):
            print "fail dis calc"
            return 0
        print "pacposaftmov" + str(pacmanSpositionAfterMoving)
        ghostPosition = self.getNextNonEatableGhost(state,pacmanSpositionAfterMoving)
        print "ghostposaftermov" + str(ghostPosition)
        pacmanDis =  self.abstractBroadSearch2(state.getWalls(), pacmanSpositionAfterMoving, closestIntX, closestIntY)[0]
        #ghostDis = 1 #self.abstractBroadSearch(state.getWalls(), ghostPosition, stopCondition)[0]
        if(ghostPosition==None):
            return 0
        return (0.1*(ghostPosition - pacmanDis))
    #def getIntersections(self, state):


    def getNextNonEatableGhost(self,state,pacmanSpositionAfterMoving):
        nonEatableGhosts = self.getNonEatableGhosts(state)
        def stopCondition(curX,curY):
            return (curX, curY) in nonEatableGhosts
        return self.abstractBroadSearch(state.getWalls(), pacmanSpositionAfterMoving, stopCondition)[0]

    def getNextEatableGhost(self, state, pacmanSpositionAfterMoving):
        powerPellets = state.getCapsules()
        nonEatableGhosts = self.getNonEatableGhosts(state)
        eatableGhosts = self.getEatableGhosts(state)
        field = state.getWalls()
        for ghost in nonEatableGhosts:
            #print ghost
            x,y = ghost
            field[int(x)][int(y)]=False
        if len(eatableGhosts) != 0:
            def stopConditionEatableGhost(curX,curY):
                return (curX, curY) in eatableGhosts
            return self.abstractBroadSearch(field, pacmanSpositionAfterMoving, stopConditionEatableGhost)[0]
        elif len(powerPellets) != 0:
            def stopConditionPallet(curX,curY):
                if (curX, curY) in powerPellets and not (curX, curY) in nonEatableGhosts:
                    return True
                else:
                    return False
            pallet = self.abstractBroadSearch(field, pacmanSpositionAfterMoving, stopConditionPallet)
            dist = pallet[0]
            pos = pallet[1]
            if pos:
                return self.getNextNonEatableGhost(state,pos) + dist
        return None

    def getStateSearch(self, state, direction, name, intersections):
        print str(intersections)
        print "--------------INTERSECTIONS"
        vecX, vecY = self.directionToCoordinate(direction)
        posX, posY = state.getPacmanPosition()
        #ghoX, ghoY = state.getGhostPosition()
        pacmanSpositionAfterMoving = (posX + vecX, posY + vecY)
        #food = state.getFood()
        #walls = state.getWalls()
        # eatableGhosts = self.getEatableGhosts(state)
        #nonEatableGhosts = self.getNonEatableGhosts(state)
        #powerPellets = state.getCapsules()
        #openList = [(posX + vecX, posY + vecY, 0)]
        #closedList = set()
        searchResult = myDict(None)
        #maxDistance = -1
        #searchResult['nearestFoodDist'] = None
        #searchResult['nearestPowerPelletDist'] = None
        #logging.debug("powerPellets = " + str(powerPellets))
        #while openList:
            #curX, curY, dist = openList.pop(0)
            #if not (curX, curY) in closedList:
                #closedList.add((curX, curY))
                #if (curX, curY) in nonEatableGhosts:
                #    logging.debug("###################################### nonEatableGhosts= " + str(nonEatableGhosts))
                #    logging.debug("###################################### state.getGhostStates = " + str(not state.getGhostStates()[0].isScared()))
                #    if not searchResult.has_key('nearestGhostDistances'):
                #        searchResult['nearestGhostDistances'] = dist
                #if (searchResult['nearestPowerPelletDist'] is None) and (curX, curY) in powerPellets and not (curX, curY) in nonEatableGhosts:
                #    searchResult['nearestPowerPelletDist'] = dist
                #    searchResult['nearestPowerPelletPos'] = (curX, curY)
                # if (curX, curY) in eatableGhosts:
                #      logging.debug("###################################### eatableGhosts= " + str(eatableGhosts))
                #      logging.debug("###################################### state.getGhostStates = " + str(state.getGhostStates()[0].isScared()))
                #     if not searchResult.has_key('nearestEatableGhostDistances'):
                #         searchResult['nearestEatableGhostDistances'] = dist
                #for (sucX, sucY) in self.getMovableDirections(curX, curY,walls):
                #    openList.append((sucX, sucY, dist + 1))
                #maxDistance = max(maxDistance, dist)
        #searchResult['nearestPowerPelletDist'] = self.getNextEatableGhost(state, pacmanSpositionAfterMoving)
        searchResult['nearestGhostDistances'] = self.getNextNonEatableGhost(state, pacmanSpositionAfterMoving)
        searchResult['nearestFoodDist'] = self.getNearestFoodPosition(state,pacmanSpositionAfterMoving)
        if(name is "r2Agent"):
            searchResult['intersectionDist'] = self.getIntersectionDistances(state,pacmanSpositionAfterMoving,intersections)
            print "intersectionDist = " + str(searchResult['intersectionDist'])
        print "nearestGhostDis = " + str(searchResult['nearestGhostDistances'])
        print "nearestFoodDis = " + str(searchResult['nearestFoodDist'])

        # if (name == 'rAgent'):
            # searchResult['intersectonDistances'] = self.getIntersectionPositions()
        #searchResult['maximumDistance'] = self.getMaximumDistance(state)

        return searchResult

    maxDistance = None
    def getMaximumDistance(self, state):
        if (RuleGenerator.maxDistance == None):
            RuleGenerator.maxDistance = (ReinforcementSearch(state)).getMaximumDistance()
        return RuleGenerator.maxDistance

    # def getIntersectionPositions(self):
    #     return self.intersections;

    def getEatableGhosts(self, state):
        eatableGhosts = []
        ghostStates = state.getGhostStates()
        for ghostState in ghostStates:
            if ghostState.isScared():
                eatableGhosts.append(ghostState.getPosition())
        logging.debug("############################################# eatableGhosts = " + str(eatableGhosts))
        return eatableGhosts

    def getNonEatableGhosts(self, state):
        nonEatableGhosts = []
        ghostStates = state.getGhostStates()
        for ghostState in ghostStates:
            if not ghostState.isScared():
                nonEatableGhosts.append(ghostState.getPosition())
        logging.debug("############################################# nonEatableGhosts = " + str(nonEatableGhosts))
        return nonEatableGhosts

    # def getAllIntersections(self, state):
    #     self.intersections = self.



    # TODO: insert features here
    def getfeatures(self, state, direction, name, intersections):
        features = myDict(0.0)
        #features['base'] = 1.0
        logging.debug("str " + str(state))
        logging.debug("dir " + str(direction))
        stateSearch = self.getStateSearch(state, direction, name, intersections)
        maxDistance = state.getWalls().width + state.getWalls().height #stateSearch['maxDistance'] #
        logging.debug("MaxDistance " + str(direction) + " " + str(maxDistance))
        if stateSearch['nearestFoodDist'] is not None:
            logging.debug("FoodDist " +  str(stateSearch['nearestFoodDist']))
            features['foodValuability'] = (float(stateSearch['nearestFoodDist'])) #/ maxDistance
        if stateSearch['nearestGhostDistances'] is not None:
            logging.debug("ghostThreat " +  str(stateSearch['nearestGhostDistances']))
            features['ghostThreat'] = (float(stateSearch['nearestGhostDistances'])) #/ maxDistance
        if stateSearch['intersections'] is not None and name is "r2Agent":
            #state.intersections = (float(stateSearch['intersections']))
            features['intersections'] = (float(stateSearch['intersections']))
#        else:
#            features['ghostThreat'] = float(maxDistance)
#        if stateSearch['nearestPowerPelletDist'] is not None:
#            logging.debug("PowerPelletDist " +  str(stateSearch['nearestPowerPelletDist']))
#            features['powerPelletValuability'] = (float(stateSearch['nearestPowerPelletDist'])) #/ maxDistance
#        else:
#            features['powerPelletValuability'] = 0.0
        # if stateSearch['nearestEatableGhostDistances'] is not None:
        #     features['eatableGhosts'] = (float(stateSearch['nearestEatableGhostDistances'])) #/ maxDistance
        #features['maxDistance'] = maxDistance
        features.normalize()
        #print str(features.normalize()) + " normalized."
        #features.divideAll(maxDistance)
        logging.debug(str(features))
        #print "fet " + str(features)
        return features

class ReinforcementRAgent(game.Agent):
    def __init__(self, numTraining = 0):
        self.name = "rAgent"
        self.actionPower = myDict(0.0)
        self.ruleGenerator = RuleGenerator()
        self.random = random.Random()
        self.lastState = None
        self.lastAction = None
        self.intersections = []
        self.alpha = 0.5
        self.gamma = 0.5
        self.epsilon = 0.1
        self.numTraining = int(numTraining)
        self.episodesSoFar = 0

    def safeListRemove(self,lst,item):
        try:
            lst.remove(item)
        except ValueError:
            pass

    def getCombinedValue(self,state, direction):
        combinedValue = 0.0
        features = self.ruleGenerator.getfeatures(state, direction, self.name, self.intersections)
        logging.debug("Features " + str(direction) + " " + str(features))
        #print "features " + str(features)
        for featureKey in features.keys():
            combinedValue += features[featureKey] * self.actionPower[featureKey]
        return combinedValue

    def updater(self,nextState):
        print " ------------- updater called ------------- "
        #print str(self.intersections)
        logging.debug("Start Updating")
        reward = self.calcReward(nextState)
        features = self.ruleGenerator.getfeatures(self.lastState, self.lastAction, self.name, self.intersections)
        combinatedValue = self.getCombinedValue(self.lastState, self.lastAction)
        maxPossibleFutureValue = self.getBestValue(nextState, self.legaldirections(nextState))
        for ruleKey in features.keys():
            # differenz
            difference = reward + self.gamma * maxPossibleFutureValue - combinatedValue
            print "differenz: " + str(difference)
            print "reward: " + str(reward)
            print "Gamma: " + str(self.gamma)
            print "maxPossibleFutureValue: " + str(maxPossibleFutureValue)
            print "combinatedValue: " + str(combinatedValue)
            logging.debug("Difference: " + str(difference))
            # gewichtung berechnen
            self.actionPower[ruleKey] = self.actionPower[ruleKey] + self.alpha * difference * features[ruleKey]
            print "actionPower" + str(self.actionPower[ruleKey] + self.alpha * difference * features[ruleKey])
            print "features rule " + str(features[ruleKey])
            #zur demo orginal QLearning
            #different = (reward + self.gamma * maxPossibleFutureValue - currentValue)
            #calcVal =  currentValue + self.alpha * different
        logging.debug("ActionPower: " + str(self.actionPower))
        #self.saving.setRatingForState(self.lastAction, self.lastState, calcVal)
        logging.debug("Stop Updating")

    def calcReward(self, state):
        return state.getScore() - self.lastState.getScore()

    def getAction(self, state):
        logging.debug("Start GetAction")
        self.lastAction = self.chooseAction(state)
        logging.debug("Action Power: " + str(self.actionPower))
        if self.isInTesting():
#            raw_input("Press Any Key ")
            pass
        logging.debug("Chosen Action: " + str(self.lastAction))
        logging.debug("Stop GetAction")
        logging.debug(str(self.lastAction))
        return self.lastAction

    def chooseAction(self, state):
        directions = self.legaldirections(state)
        logging.debug(str(directions))
        rnd = self.random.random()
        if self.epsilon > rnd:
            return self.random.choice(directions)
        else:
            return self.getBestDirection(self.lastState, directions)

    def legaldirections(self, state):
        directions = state.getLegalPacmanActions()
        self.safeListRemove(directions, Directions.LEFT)
        self.safeListRemove(directions, Directions.REVERSE)
        self.safeListRemove(directions, Directions.RIGHT)
        # self.safeListRemove(directions, Directions.STOP)
        return directions

    def getBestDirection(self, state, directions):
        bestVal = float('-inf')
        bestDirection = None
        logging.debug("Possible Directions" + str(directions))
        for direction in directions:
            tmpValue = self.getCombinedValue(state, direction)
            logging.debug("Combinated Value " + str(direction) + " " + str(tmpValue))
            logging.debug(str(tmpValue))
            if bestVal < tmpValue:
                bestVal = tmpValue
                bestDirection = direction
        return bestDirection

    def getBestValue(self, state, directions):
        bestDirection = self.getBestDirection(state,directions)
        if bestDirection:
            return self.getCombinedValue(state, bestDirection)
        else:
            return 0.0

    def observationFunction(self, state, intersections):
        if self.lastState:
            self.updater(state)
        else:
            if not self.isInTraining():
               self.epsilon = 0.0
               self.alpha = 0.0
               pass
        self.lastState = state
        #raw_input("Press Any Key ")
        return state

    def final(self, state):
        self.updater(state)
        self.lastState = None
        self.lastAction = None
        #raw_input("Press Any Key ")
        if self.isInTraining():
            self.episodesSoFar += 1
            logging.info("Training " + str(self.episodesSoFar) + " of " + str (self.numTraining))
        else:
            self.epsilon = 0.0
            self.alpha = 0.0
            if state.isLose():
                #raw_input("Press Any Key ")
                pass

    def isInTraining(self):
        return self.episodesSoFar < self.numTraining

    def isInTesting(self):
        return not self.isInTraining()

class ReinforcementRAgent2(game.Agent):
    def __init__(self, numTraining = 0):
        self.name = "1r2Agent"
        self.actionPower = myDict(0.0)
        self.ruleGenerator = RuleGenerator()
        self.random = random.Random()
        self.lastState = None
        self.lastAction = None
        self.intersections = []
        self.alpha = 0.5
        self.gamma = 0.5
        self.epsilon = 0.1
        self.numTraining = int(numTraining)
        self.episodesSoFar = 0

    def safeListRemove(self,lst,item):
        try:
            lst.remove(item)
        except ValueError:
            pass

    def getCombinedValue(self,state, direction):
        combinedValue = 0.0
        features = self.ruleGenerator.getfeatures(state, direction, self.name, self.intersections)
        logging.debug("Features " + str(direction) + " " + str(features))
        #print "features " + str(features)
        for featureKey in features.keys():
            combinedValue += features[featureKey] * self.actionPower[featureKey]
        return combinedValue

    def updater(self,nextState):
        print " ------------- updater called ------------- "
        #print str(self.intersections)
        logging.debug("Start Updating")
        reward = self.calcReward(nextState)
        features = self.ruleGenerator.getfeatures(self.lastState, self.lastAction, self.name, self.intersections)
        combinatedValue = self.getCombinedValue(self.lastState, self.lastAction)
        maxPossibleFutureValue = self.getBestValue(nextState, self.legaldirections(nextState))
        for ruleKey in features.keys():
            # differenz
            difference = reward + self.gamma * maxPossibleFutureValue - combinatedValue
            print "differenz: " + str(difference)
            print "reward: " + str(reward)
            print "Gamma: " + str(self.gamma)
            print "maxPossibleFutureValue: " + str(maxPossibleFutureValue)
            print "combinatedValue: " + str(combinatedValue)
            logging.debug("Difference: " + str(difference))
            # gewichtung berechnen
            self.actionPower[ruleKey] = self.actionPower[ruleKey] + self.alpha * difference * features[ruleKey]
            print "actionPower" + str(self.actionPower[ruleKey] + self.alpha * difference * features[ruleKey])
            print "features rule " + str(features[ruleKey])
            #zur demo orginal QLearning
            #different = (reward + self.gamma * maxPossibleFutureValue - currentValue)
            #calcVal =  currentValue + self.alpha * different
        logging.debug("ActionPower: " + str(self.actionPower))
        #self.saving.setRatingForState(self.lastAction, self.lastState, calcVal)
        logging.debug("Stop Updating")

    def calcReward(self, state):
        return state.getScore() - self.lastState.getScore()

    def getAction(self, state):
        logging.debug("Start GetAction")
        self.lastAction = self.chooseAction(state)
        logging.debug("Action Power: " + str(self.actionPower))
        if self.isInTesting():
#            raw_input("Press Any Key ")
            pass
        logging.debug("Chosen Action: " + str(self.lastAction))
        logging.debug("Stop GetAction")
        logging.debug(str(self.lastAction))
        return self.lastAction

    def chooseAction(self, state):
        directions = self.legaldirections(state)
        logging.debug(str(directions))
        rnd = self.random.random()
        if self.epsilon > rnd:
            return self.random.choice(directions)
        else:
            return self.getBestDirection(self.lastState, directions)

    def legaldirections(self, state):
        directions = state.getLegalPacmanActions()
        self.safeListRemove(directions, Directions.LEFT)
        self.safeListRemove(directions, Directions.REVERSE)
        self.safeListRemove(directions, Directions.RIGHT)
        # self.safeListRemove(directions, Directions.STOP)
        return directions

    def getBestDirection(self, state, directions):
        bestVal = float('-inf')
        bestDirection = None
        logging.debug("Possible Directions" + str(directions))
        for direction in directions:
            tmpValue = self.getCombinedValue(state, direction)
            logging.debug("Combinated Value " + str(direction) + " " + str(tmpValue))
            logging.debug(str(tmpValue))
            if bestVal < tmpValue:
                bestVal = tmpValue
                bestDirection = direction
        return bestDirection

    def getBestValue(self, state, directions):
        bestDirection = self.getBestDirection(state,directions)
        if bestDirection:
            return self.getCombinedValue(state, bestDirection)
        else:
            return 0.0

    def observationFunction(self, state, intersections):
        self.intersections = intersections
        if self.lastState:
            self.updater(state)
        else:
            if not self.isInTraining():
               self.epsilon = 0.0
               self.alpha = 0.0
               pass
        self.lastState = state
        #raw_input("Press Any Key ")
        return state

    def final(self, state):
        self.updater(state)
        self.lastState = None
        self.lastAction = None
        #raw_input("Press Any Key ")
        if self.isInTraining():
            self.episodesSoFar += 1
            logging.info("Training " + str(self.episodesSoFar) + " of " + str (self.numTraining))
        else:
            self.epsilon = 0.0
            self.alpha = 0.0
            if state.isLose():
                #raw_input("Press Any Key ")
                pass

    def isInTraining(self):
        return self.episodesSoFar < self.numTraining

    def isInTesting(self):
        return not self.isInTraining()
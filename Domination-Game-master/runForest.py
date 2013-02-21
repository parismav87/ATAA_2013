import sys
import core
import random
import math
import cPickle as pickle
class Agent(object):
    
    NAME = "default_agent"
    
    def __init__(self, id, team, settings=None, field_rects=None, field_grid=None, nav_mesh=None, blob=None):
        self.id = id
        self.team = team
        self.mesh = nav_mesh
        self.grid = field_grid
        self.settings = settings
        self.previousState = None
        self.previousAction = None
        self.previousCPS = None
        self.goal = None
        self.gamma = 0.5
        self.alpha = 0.7
        self.epsilon = 0.2
        self.callsign = '%s-%d'% (('BLU' if team == TEAM_BLUE else 'RED'), id)

        if os.path.isfile("runForest.pck"):
            file = open("runForest.pck", "r")
            self.qtable = pickle.load(file)
            file.close()                                    
        else:
            self.qtable = self.createQTable()

    
    def observe(self, observation):
        """ Each agent is passed an observation using this function,
            before being asked for an action. You can store either
            the observation object or its properties to use them
            to determine your action. Note that the observation object
            is modified in place.
        """
        self.observation = observation
        self.selected = observation.selected
            
        if observation.selected:
            print observation

    def createQTable(self):
        Qtable = dict()
        for i in range(28):
            for j in range(16):
                Qtable[i,j] = dict()
                for c1 in range(-1,2):
                    for c2 in range(-1,2):
                        Qtable[i,j][c1,c2] = dict()
                        for ai in range(-2,3):
                            for aj in range(-2,3):
                                Qtable[i,j][c1,c2][i+ai,j+aj] = 20.0
        return Qtable

    def state_position(self, state):
        """ This function returns the middle state_position
            in an input state grid position
        """
        x = math.floor((state[0]*16+(state[0]+1)*16)/2)
        y = math.floor((state[1]*16+(state[1]+1)*16)/2)
        return [x,y]

    def drive(self, current_state, goalLoc):
        goalLoc = self.state_position(goalLoc)
        loc = self.state_position(current_state)
        dx = goalLoc[0]-loc[0]
        dy = goalLoc[1]-loc[1]
        turn = angle_fix(math.atan2(dy, dx) - self.observation.angle)
        speed = 10*(dx**2 + dy**2)**0.5
        shoot = 0
        return (turn, speed, shoot)

    def reward_function(self, cps):
        reward_NEW = 0
        reward_OLD = 0
        for i in range(len(cps)):
            reward_NEW += cps[i]

        if self.previousCPS is not None:
            for i in range(len(self.previousCPS)):
                reward_OLD += self.previousCPS[i]


        return reward_NEW

    def eGreedy(self, current_state, cps):
        moves = []
        for i in range(-2,3):
            for j in range(-2,3):
                position = (current_state[0]+i, current_state[1]+j)
                moves.append(position)

        if random.random() < self.epsilon :
            r = math.floor(random.random() * len(moves))
            return (moves[int(r)][0], moves[int(r)][1])
        else:
            bestMoves = []
            bestValue = 0.0
            for move in moves:
                value = self.qtable[current_state][cps][move]
                if value > bestValue:
                    bestMoves = []
                    bestMoves.append(move)
                    bestValue = value
                    action  = move
                if value == bestValue:
                    bestMoves.append(move)
            r = math.floor(random.random() * len(bestMoves))
            return (bestMoves[int(r)][0], bestMoves[int(r)][1])


    def check_cps(self):
        """ Check the control points and return the state of these
            control points.
            1 is ours
            0 is neutral
            -1 is opponent's
        """
        controlPoint1 = 0
        controlPoint2 = 0
        if self.observation.cps[0][2] == 1:
            controlPoint1 += 1
        if self.observation.cps[0][2] == 0:
            controlPoint1 -= 1
        if self.observation.cps[1][2] == 1:
            controlPoint2 += 1
        if self.observation.cps[1][2] == 0:
            controlPoint2 -= 1
        return (controlPoint1,controlPoint2)

    def returnMaxValue(self,current_state, cps):
        MaxValue = 0
        obs = self.observation
        for action, value in self.qtable[current_state][cps].iteritems():
            if value > MaxValue:
                MaxValue = value
        return MaxValue

    def action(self):
        # take observation
        obs = self.observation
        # translate cps to state variable
        cps = self.check_cps()
        # determine the current state
        current_state = (obs.loc[0]/16,obs.loc[1]/16)    
        # select from the actions with eGreedy action selection
        action = self.eGreedy(current_state, cps)
        # # Q-learning update rule
        # get reward for current state action pair
        reward = self.reward_function(cps)
        # get the max potential value from next state
        maxValue = self.returnMaxValue(current_state, cps)

        print reward

        if self.previousState is not None:                        
            self.qtable[self.previousState][self.previousCPS][self.previousAction] = self.qtable[self.previousState][self.previousCPS][self.previousAction] 
            + self.alpha * (reward + self.gamma * maxValue - self.qtable[self.previousState][self.previousCPS][self.previousAction])
        # given the action drive the tank to this position
        drive = self.drive(current_state, action)
        # action assigned to the agent
        self.previousState = current_state
        self.previousAction = action
        self.previousCPS = cps
        return drive
        
        
    def finalize(self, interrupted=False):
        """ This function is called after the game ends, 
            either due to time/score limits, or due to an
            interrupt (CTRL+C) by the user. Use it to
            store any learned variables and write logs/reports.
        """
        file = open("runForest.pck", "w") # write mode
        pickle.dump(self.qtable, file)
        file.close()
        

import sys
import core
import random
import math
class Agent(object):
    
    NAME = "default_agent"
    
    def __init__(self, id, team, settings=None, field_rects=None, field_grid=None, nav_mesh=None, blob=None):
        self.id = id
        self.team = team
        self.mesh = nav_mesh
        self.grid = field_grid
        self.settings = settings
        self.goal = None
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
        for i in range(29):
            for j in range(16):
                Qtable[i,j] = dict()
                for c1 in range(-1,2):
                    for c2 in range(-1,2):
                        Qtable[i,j][c1,c2] = dict()
                        for ai in range(-2,3):
                            for aj in range(-2,3):
                                Qtable[i,j][c1,c2][i+ai,j+aj] = 200.0
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
        reward = 0
        for i in range(len(cps)):
            reward += cps[i] * 100
        return reward

    def move_list(self):
        location = self.observation.loc
        walls = self.observation.walls
        moves = []
        for i in range(-2,3):
            for j in range(-2,3):
                if(walls[2+i][2+j] == 0):
                    position = [(location[0]/16) + j, (location[1]/16) + i]
                    moves.append(position)
        return moves

    def eGreedy(self, moves, cps, e):
        if random.random() < 0.1 :
            r = math.floor(random.random() * len(moves))
            return moves[int(r)]
        else:
            bestMoves = []
            bestValue = 0.0
            for move in moves:
                print move
                value = self.qtable[self.observation.loc[0]/16, self.observation.loc[1]/16][cps][move[0], move[1]]
                action = move
                if value > bestValue:
                    bestValue = value
                    bestMoves = []
                    bestMoves.append(action)
                if value == bestValue:
                    bestMoves.append(action)
            r = math.floor(random.random() * len(bestMoves))
            return bestMoves[int(r)]



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

    def returnMaxValue(self, cps):
        MaxValue = 0
        obs = self.observation
        for action, value in self.qtable[obs.loc[0]/16, obs.loc[1]/16][cps].iteritems():
            if value > MaxValue:
                MaxValue = value
        return MaxValue

    def action(self):
        # take observation
        obs = self.observation
        # translate cps to state variable
        cps = self.check_cps()
        # determine the current state
        current_state = [obs.loc[0]/16,obs.loc[1]/16],[cps]
        # if first step previous state is the same as current
        if obs.step == 1:
            previous_state = [obs.loc[0]/16,obs.loc[1]/16],[cps]
        # return the possible movements that agent can do
        possible_moves = self.move_list()
        # select from the actions with eGreedy action selection
        action = self.eGreedy(possible_moves, cps, 0.1)

        # # Q-learning update rule
        # reward = self.reward_function(cps)
        # maxValue = self.returnMaxValue(cps)
        # print maxValue
        # print self.qtable[current_state[0][0],current_state[0][1]][cps[0], cps[1]][action[0], action[1]]


        # given the action drive the tank to this position
        drive = self.drive(current_state[0], action)
        # action assigned to the agent
        previous_state = current_state
        return drive
        
        
    def finalize(self, interrupted=False):
        """ This function is called after the game ends, 
            either due to time/score limits, or due to an
            interrupt (CTRL+C) by the user. Use it to
            store any learned variables and write logs/reports.
        """
        pass
        file = open("runForest.pck", "w") # write mode
        pickle.dump(self.qtable, file)
        file.close()
        

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
            file = open("runForest.pck", "r") # read mode
            self.qtable = pickle.load(file)
            file.close()
        else:
            print "nope"
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
                for ai in range(-2,3):
                    for aj in range(-2,3):
                        Qtable[i,j][i+ai,j+aj] = 10.0
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

    def reward_function(current, previous):
        pass

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

    def eGreedy(self, moves, e):
        if random.random() < 0.1 :
            r = math.floor(random.random() * len(moves))
            return moves[int(r)]
        else:
            bestMoves = []
            bestValue = 0.0
            for action, value in self.qtable[self.observation.loc[0]/16,self.observation.loc[1]/16].iteritems():
                if value > bestValue:
                    bestValue = value
                    bestMoves = []
                    bestMoves.append(action)
                if value == bestValue:
                    bestMoves.append(action)
            r = math.floor(random.random() * len(bestMoves))
            return bestMoves[int(r)]

    def action(self):
        obs = self.observation
        current_state = [obs.loc[0]/16,obs.loc[1]/16]
        if obs.step == 1:
            previous_state = [obs.loc[0]/16,obs.loc[1]/16]

        possible_moves = self.move_list()
        action = self.eGreedy(possible_moves, 0.1)
        drive = self.drive(current_state, action)
        # action assigned to the agent
        previous_state = current_state
        return drive


    def debug(self, surface):
        """ Allows the agents to draw on the game UI,
            Refer to the pygame reference to see how you can
            draw on a pygame.surface. The given surface is
            not cleared automatically. Additionally, this
            function will only be called when the renderer is
            active, and it will only be called for the active team.
        """
        import pygame
        # First agent clears the screen
        surface.fill((0,0,0,0))
        # Selected agents draw their info
        if self.goal is not None:
            surface.draw.circle(surface, (255,255,255), self.observation.loc, 16, 1)
        
        
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
        

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
    
    def observe(self, observation):
        self.observation = observation
        self.selected = observation.selected

        if observation.selected:
            print observation

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
        speed = (dx**2 + dy**2)**0.5
        shoot = 0
        return (turn, speed, shoot)

    def reward_function(current, previous):
        pass

    def move_list(self):
        location = self.observation.loc
        moves = []
        for i in range(-1,2):
            for j in range(-1,2):
                position = [(location[0]/16) + i, (location[1]/16) + j]
                moves.append(position)
        return moves

    def action_selection(self, moves):
        pass
        r = math.floor(random.random() * len(moves))
        return moves[int(r)]

    def action(self):
        obs = self.observation
        current_state = [obs.loc[0]/16,obs.loc[1]/16]
        if obs.step == 1:
            previous_state = [obs.loc[0]/16,obs.loc[1]/16]

        possible_moves = self.move_list()
        action = self.action_selection(possible_moves)
        drive = self.drive(current_state, action)
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
        

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

    def drive(self):
        pass

    def reward_function(current, previous):
        pass

    def state_position(state):
        """ This function returns the middle state_position
            in an input state grid position
        """
        x = (state[0]*16+(state[0]+1)*16)/2
        y = (state[1]*16+(state[1]+1)*16)/2
        return [x,y]

    def move_list(state):
        moves = []
        for i in range(-1,2):
            for j in range(-1,2):
                position = [state[0]+i, state[1]+j]
                moves.append(position)
        return moves

    def action_selection(moves):
        r = math.floor(random.random() * len(moves))
        return moves[r]

    def action(self):
        obs = self.observation
        f = open("test.txt",'a')
        current_state = [obs.loc[0]/16,obs.loc[1]/16]
        if obs.step == 1:
            previous_state = [obs.loc[0]/16,obs.loc[1]/16]

        # possible_moves = self.move_list(current_state)
        # action = action_selection(possible_moves)
        # f.write(str(action)+'\n')
        # f.close()
        # action assigned to the agent
        turn = 0
        speed = 0
        shoot = 0

        previous_state = [obs.loc[0]/16,obs.loc[1]/16]
        return (turn,speed,shoot)
        
    def finalize(self, interrupted=False):
        """ This function is called after the game ends, 
            either due to time/score limits, or due to an
            interrupt (CTRL+C) by the user. Use it to
            store any learned variables and write logs/reports.
        """
        pass
        

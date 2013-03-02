import itertools as it

class Agent(object):
    
    NAME = "Django"
    
    def __init__(self, id, team, settings=None, field_rects=None, field_grid=None, nav_mesh=None, blob=None, **kwargs):
        """ Each agent is initialized at the beginning of each game.
            The first agent (id==0) can use this to set up global variables.
            Note that the properties pertaining to the game field might not be
            given for each game.
        """
        self.id = id
        self.team = team
        self.mesh = nav_mesh
        self.grid = field_grid
        self.settings = settings
        self.goalState = None
        self.previouState = None
        self.callsign = '%s-%d'% (('BLU' if team == TEAM_BLUE else 'RED'), id)
        self.blobpath = "agents/django_"+self.callsign
        self.speed = None
        

        # Recommended way to share variables between agents.
        if id == 0:
            self.all_agents = self.__class__.all_agents = []
        self.all_agents.append(self)

        # state space -- positions on the grid for x axis
        self.states = [(232,56),(264,216),(184,168),(312,104)]

        if self.id == 0:
            if os.path.isfile(self.blobpath):
                file = open(self.blobpath, "rb")
                self.__class__.qtable = pickle.load(file)
                file.close()                                    
            else:
                self.__class__.qtable = self.createQTable()

    def createQTable(self):
        Qtable = dict()
        n_of_agents = 3
        pos = it.product(self.states, repeat = n_of_agents)
        for p in pos:
            print p
            Qtable[p] = dict()
            cps_con = [-1, 0, 1]
            cps = it.product(cps_con,cps_con, repeat = 1)
            for c in cps:  
                Qtable[p][c] = dict()
                foes_con = range(0,4)
                foes = it.product(foes_con, repeat = 4)
                for f in foes:
                    Qtable[p][c][f] = dict()
                    actions_con = [-1, 0, 1]
                    actions = it.product(actions_con,actions_con, repeat = 1)
                    for a in self.states:
                        Qtable[p][c][f][a] = 20.0
        return Qtable
    
    def observe(self, observation):
        """ Each agent is passed an observation using this function,
            before being asked ffoes_conor an action. You can store either
            the observation object or its properties to use them
            to determine your action. Note that the observation object
            is modified in place.
        """
        self.observation = observation
        self.selected = observation.selected

        if observation.selected:
            print observation

    def eGreedy(self, current_state, cps):
        pass

    def stateMaxValue(self,current_state, cps):
        pass

    def find_state(self, location):
        for state in self.states:
            if point_dist(state, location) < self.settings.tilesize:
                return state
        return None

    def shoot(self, obs):
        # Shoot enemies
        shoot = False
        if (obs.ammo > 0 and 
            obs.foes and 
            point_dist(obs.foes[0][0:2], obs.loc) < self.settings.max_range and
            not line_intersects_grid(obs.loc, obs.foes[0][0:2], self.grid, self.settings.tilesize)):
            self.goalState = obs.foes[0][0:2]
            shoot = True
        return shoot

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

    def check_foes(self, team):
        foes_table = [0,0,0,0]
        foes = dict()
        for agent in team:
            for foe in agent.observation.foes:
                if foe[0:2] in foes:
                    pass
                else:
                    foes[foe[0:2]] = 1
        for item, value in foes.iteritems():
            for i in range(len(self.states)):
                 if point_dist(self.states[i], item) < 3.0 * self.settings.tilesize:
                     foes_table[i] += 1
                            
        return foes_table

    def check_friends(self):
        friends = []
        friends.append(self.previouState)
        for team_obs in self.all_agents:
            if team_obs.id != self.id:
                friends.append(team_obs.previouState)
        return friends

    def drive_tank(self, obs):
        # Compute path, angle and drive
        path = find_path(obs.loc, self.goalState, self.mesh, self.grid, self.settings.tilesize)
        if path:
            dx = path[0][0] - obs.loc[0]
            dy = path[0][1] - obs.loc[1]
            turn = angle_fix(math.atan2(dy, dx) - obs.angle)
            speed = (dx**2 + dy**2)**0.5
            if turn > self.settings.max_turn or turn < -self.settings.max_turn:
                shoot = False
            if abs(math.degrees(turn)) >= 45:
                if self.speed is not None:
                    speed = max(0.9 * self.speed, 1)
            
        else:
            turn = 0
            speed = 0
        self.speed = speed
        return (turn, speed)
                    
    def action(self):
        """ This function is called every step and should
            return a tuple in the form: (turn, speed, shoot)
        """
        # take the self observation
        obs = self.observation
        # check the control points
        cps = self.check_cps()
        # check the enemies
        foes = self.check_foes(self.all_agents)
        # check the positions of agent's friends
        friends = self.check_friends()

        not_none = True
        for item in friends:
            if item is None:
                not_none = False
        if not_none:
            fr = (friends[0],friends[1],friends[2])
            fo = (foes[0],foes[1],foes[2],foes[3])
            print self.__class__.qtable[fr][cps][fo]


        # Check if agent reached goalState.
        if self.goalState is not None and point_dist(self.goalState, obs.loc) < self.settings.tilesize:
            self.previouState = self.find_state(self.goalState)
            # value table needs to be updated...
            self.goalState = None

        shoot = self.shoot(obs)
        # agent reach its goalState, should be assigned a new action
        if self.goalState is None:
            self.goalState = self.states[random.randint(0,len(self.states)-1)]

        drive = self.drive_tank(obs)

        return (drive[0], drive[1], shoot)
        
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
        if self.id == 0:
            surface.fill((0,0,0,0))
        # Selected agents draw their info
        if self.selected:
            if self.goalState is not None:
                pygame.draw.line(surface,(0,0,0),self.observation.loc, self.goalState)
        
    def finalize(self, interrupted=False):
        """ This function is called after the game ends, 
            either due to time/score limits, or due to an
            interrupt (CTRL+C) by the user. Use it to
            store any learned variables and write logs/reports.
        """
        if self.blobpath is not None:
            if self.id == 0:
                try:
                    print "writing the q table back..."
                    file = open(self.blobpath, "wb")
                    pickle.dump(self.__class__.qtable, file)
                    file.close()
                except:
                    # We can't write to the blob, this is normal on AppEngine since
                    # we don't have filesystem access there.        
                    print "Agent %s can't write blob." % self.callsign
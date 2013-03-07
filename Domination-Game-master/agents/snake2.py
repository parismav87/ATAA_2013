import itertools as it
import cPickle as pickle

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
        self.goal = None
        self.callsign = '%s-%d'% (('BLU' if team == TEAM_BLUE else 'RED'), id)
        self.blobpath = "agents/django_"+self.callsign
        self.speed = None
        # Recommended way to share variables between agents.
        if id == 0:
            self.all_agents = self.__class__.all_agents = []
        self.all_agents.append(self)

        # state space -- positions on the grid for x axis
        self.states = [(232,56),(264,216),(312,104),(184,168)]
    
    def observe(self, observation):
        """ Each agent is passed an observation using this function,
            before being asked ffoes_conor an action. You can store either
            the observation object or its properties to use them
            to determine your action. Note that the observation object
            is modified in place.
        """
        self.observation = observation
        if self.team == TEAM_BLUE:
            print observation.angle;
        self.selected = observation.selected
        if observation.selected:
            print observation



    def shoot(self):
        # Shoot enemies
        obs = self.observation
        shoot = False
        if (obs.ammo > 0 and 
            obs.foes and 
            point_dist(obs.foes[0][0:2], obs.loc) < self.settings.max_range and
            not line_intersects_grid(obs.loc, obs.foes[0][0:2], self.grid, self.settings.tilesize)):
            self.goal = obs.foes[0][0:2]
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


    def drive_tank(self):
        obs = self.observation
        # Compute path, angle and drive
        path = find_path(obs.loc, self.goal, self.mesh, self.grid, self.settings.tilesize)
        if path:
            dx = path[0][0] - obs.loc[0]
            dy = path[0][1] - obs.loc[1]
            turn = angle_fix(math.atan2(dy, dx) - obs.angle)
            speed = (dx**2 + dy**2)**0.5
            if turn > self.settings.max_turn or turn < -self.settings.max_turn:
                shoot = False
            if abs(math.degrees(turn)) >= 45:
                if self.speed is not None:
                    speed = max(0.7 * self.speed, 1)  
        else:
            turn = 0
            speed = 0
        self.speed = speed
        return (turn, speed)

    def normAngle(self,angle):
        ang = (2*3.14 + angle)%(2*3.14);
        return ang;

    def canShoot(self):
        obs = self.observation;
        for foe in obs.foes:
            dx = foe[0] - obs.loc[0]
            dy = foe[1] - obs.loc[1]
            angle = math.atan2(dy, dx);
            print "malakaaa %f" % angle 
            angle = self.normAngle(angle);
            obsangle = self.normAngle(obs.angle);
            da = (obsangle-angle)
            print math.degrees(da);
            dist = (dx**2 + dy**2)**0.5
            if obs.ammo>0 and abs(math.degrees(da))<= 45 and dist<=self.settings.max_range and not line_intersects_grid(obs.loc, foe[0:2], self.grid, self.settings.tilesize):   
                    return (da,0,True)
        return False

    def action(self):
        """ This function is called every step and should
            return a tuple in the form: (turn, speed, shoot)
        """

        # take the self observation
        obs = self.observation
        # check if goal is reached
        if self.goal is not None and point_dist(self.goal, obs.loc) < self.settings.tilesize:
            self.goal = None
        
        # Walk to random CP
        if self.goal is None:
            self.goal = self.states[random.randint(0,len(self.states)-1)]


        drive = self.drive_tank()
        shoot = self.shoot()
        if not self.canShoot():
            return (drive[0],drive[1],shoot)
        return self.canShoot();

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
            if self.goal is not None:
                pygame.draw.line(surface,(0,0,0),self.observation.loc, self.goal)
        
    def finalize(self, interrupted=False):
        """ This function is called after the game ends, 
            either due to time/score limits, or due to an
            interrupt (CTRL+C) by the user. Use it to
            store any learned variables and write logs/reports.
        """
        print "The end..."
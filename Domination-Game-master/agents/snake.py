import itertools as it
import cPickle as pickle

FIELD = """w w w w w w w w w w w w w w w w w w w w w w w w w w w w w w w
w _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ w
w _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ w
w _ _ _ _ _ _ _ _ _ _ _ _ _ S _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ w
w _ _ _ _ _ _ # _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ # _ _ _ _ _ _ w
w _ _ _ _ _ _ _ W w w w w w w w w w w w w w W _ _ # _ # _ _ w
w _ _ _ W _ _ _ w _ _ _ _ _ _ _ _ _ _ S _ _ _ # _ _ W _ _ _ w
w _ _ _ w _ _ _ w _ _ _ # _ _ _ _ _ # _ _ # _ # _ _ w _ _ _ w
w _ _ _ w _ _ _ W _ _ _ _ W w w w W _ _ _ _ W _ _ _ w _ _ S w
w _ _ _ w _ _ # _ # _ _ # _ _ _ _ _ # _ _ _ w _ _ _ w _ _ _ w
w _ _ _ W _ _ # _ # _ S _ _ _ _ _ _ _ _ _ _ w _ _ _ W _ _ _ w
w _ _ _ _ _ _ _ W w w w w w w w w w w w w w W _ _ # _ # _ _ w
w _ _ _ _ _ _ # _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ # _ _ _ _ _ _ w
w _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ S _ _ _ _ _ _ _ _ _ _ _ _ _ w
w _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ w
w _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ w
w w w w w w w w w w w w w w w w w w w w w w w w w w w w w w w"""

class Node(object):
    def __init__(self):
        self.data = None
        self.childs = None
        self.sumDistance = 0.0
        self.sumTurn = 0.0
        self.orientation = 0.0
        self.terminal = False
        self.parent = None

class Path(object):
    def __init__(self):
        self.path = None
        self.turn = None
        self.distance = None

class Agent(object):
    
    NAME = "BlackMamba"
    """
    The black mamba (Dendroaspis polylepis), also called the common black mamba or black-mouthed mamba,
    is the longest venomous snake in Africa. It is the fastest snake in the world, capable of moving at
    4.32 to 5.4 metres per second. It has a reputation for being aggressive and highly venomous and is 
    among the world's most venomous land snakes.
    """
    
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
        self.map_width = 0
        self.map_height = 0
        self.map = self.create_map()
        self.path_points = None
        self.states = None
        self.path = None
        self.previous_goal = None
        self.find_path_state_points()
        self.walls = self.find_walls()
        if self.id == 0:
            self.createQTable()
        self.ff = 0
        self.counter = 0


    def createQTable(self):
        Qtable = dict()
        n_of_agents = 3 
        transitions = it.combinations(self.states, 2)
        state_space = it.chain(self.states, transitions)
        pos = it.product(state_space, repeat = n_of_agents)
        counter = 0
        for p in pos:
            Qtable[p] = dict()
            cps_con = [-1, 0, 1]
            cps = it.product(cps_con,cps_con, repeat = 1)
            for c in cps:  
                Qtable[p][c] = dict()
                for a in self.states:
                    Qtable[p][c][a] = 20.0
                    counter += 1
        print counter



    def create_map(self):
        x = 0
        y = 0
        mapp = {}
        for char in FIELD:
            if char == "\n":
                y += 1
                x = 0
            elif char == " ":
                pass
            else:
                mapp[x,y] = char
                x += 1
        self.map_width = x
        self.map_height = y + 1
        return mapp

    def find_path_state_points(self):
        points = []
        states = []
        for x in xrange(self.map_width):
            for y in xrange(self.map_height):
                if self.map[x,y] == "#":
                    points.append((x*16.0 + 8.0, y*16.0 + 8.0))
                if self.map[x,y] == "S":
                    states.append((x*16.0 + 8.0, y*16.0 + 8.0))
        self.states = states
        self.path_points = points

    def wall_end(self, x, y, dx, dy):
        if self.map[x+dx,y+dy] != "w":
            return None
        else:
            x += dx
            y += dy
            while self.map[x,y] != "W" and self.map[x,y] == "w":
                x += dx
                y += dy
            return (x,y)


    def find_walls(self):
        walls = []
        for x in xrange(self.map_width):
            for y in xrange(self.map_height):
                if self.map[x,y] == "W":
                    start = (x,y)
                    end = []
                    end.append(self.wall_end(x,y,1,0))
                    end.append(self.wall_end(x,y,-1,0))
                    end.append(self.wall_end(x,y,0,1))
                    end.append(self.wall_end(x,y,0,-1))
                    for ending in end:
                        if ending is not None:
                            exist = False
                            if len(walls) > 0:
                                for wall in walls:
                                    if (start[0] == wall[0] and start[1] == wall[1] and ending[0] == wall[2] and ending[1] == wall[3]) or (ending[0] == wall[0] and ending[1] == wall[1] and start[0] == wall[2] and start[1] == wall[3]):
                                        exist = True
                            if not exist:
                                walls.append((start[0],start[1],ending[0],ending[1]))
        return walls


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

    def equal(self, point1, point2):
        if point1[0] == point2[0] and point1[1] == point2[1]:
            return True
        return False

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

    def find_awesome_path(self):

        obs = self.observation

        if not line_intersects_grid(obs.loc, self.goal, self.grid, self.settings.tilesize):
            return [self.goal, obs.loc]
        else:
            temp_points = self.path_points
            # create the root element of the tree
            root = Node()
            root.data = obs.loc
            root.terminal = False
            root.parent = None
            root.orientation = obs.angle
            temp = root
            level = list()
            level_nodes = list()
            level_nodes.append(root)
            level.append(level_nodes)
            generated_paths = list()
            while len(generated_paths) <= 1:
                # if a path is found and the tree depth is growing a lot
                # we keep the only path and stop exploring
                new_lvl_nodes = list()
                for node in level[len(level)-1]:
                    explore = True
                    # cost so far for the current node
                    cost = node.sumDistance + 75.0 * node.sumTurn
                    # if there are paths already, nodes in the tree have to have
                    # less cost than the path in order to be explored
                    if len(generated_paths) > 0:
                        for path in generated_paths:
                            path_cost = path.distance + 75.0 * path.turn
                            if cost >= path_cost:
                                explore = False
                    else:
                        if cost > 400:
                            explore = False

                    if explore:
                        if not node.terminal:
                            if node.childs is None:
                                node.childs = list()
                                for point in temp_points:
                                    family_issues = self.family_issues(node, point)
                                    if not family_issues:
                                        if not line_intersects_grid(node.data, point, self.grid, self.settings.tilesize):
                                            tmp = Node()
                                            tmp.data = point
                                            tmp.parent = node
                                            tmp.sumDistance = node.sumDistance + point_dist(point, node.data)
                                            dx = point[0] - node.data[0]
                                            dy = point[1] - node.data[1]
                                            tmp.sumTurn += abs(angle_fix(math.atan2(dy, dx) - node.orientation))
                                            tmp.orientation = angle_fix(math.atan2(dy, dx))
                                            node.childs.append(tmp)
                                            new_lvl_nodes.append(tmp)

                                if not line_intersects_grid(node.data, self.goal, self.grid, self.settings.tilesize):
                                    tmp = Node()
                                    tmp.data = self.goal
                                    tmp.parent = node
                                    tmp.sumDistance = node.sumDistance + point_dist(self.goal, node.data)
                                    dx = self.goal[0] - node.data[0]
                                    dy = self.goal[1] - node.data[1]
                                    tmp.sumTurn += abs(angle_fix(math.atan2(dy, dx) - node.orientation))
                                    tmp.orientation = angle_fix(math.atan2(dy, dx))
                                    node.childs.append(tmp)
                                    new_lvl_nodes.append(tmp)
                                    generated_paths.append(self.rollback_path(tmp))
                                    tmp.terminal = True

                level.append(new_lvl_nodes)
            optimalPath = self.chooseOptPath(generated_paths)
            return optimalPath

    def family_issues(self, node, candidatePoint):
        temp = node
        if self.equal(candidatePoint, temp.data):
            return True
        while temp.parent is not None:
            if self.equal(candidatePoint, temp.data):
                return True
            temp = temp.parent
        if self.equal(candidatePoint, temp.data):
                return True
        return False

    def chooseOptPath(self, candidatePaths):
        optimalPath = None
        optimalCost = float('inf')
        for path in candidatePaths:
            cost = path.distance + 75.0 * path.turn
            if cost < optimalCost:
                optimalCost = cost
                optimalPath = path
        return optimalPath.path

    def rollback_path(self, node):
        p = Path()
        path = []
        temp = node
        p.distance = node.sumDistance
        p.turn = node.sumTurn
        counter = 0
        while temp.parent is not None:
            path.append(temp.data)
            temp = temp.parent
        path.append(temp.data)
        p.path = path
        return p

    def drive_tank(self):
        obs = self.observation
        # Compute path, angle and drive
        if self.previous_goal != self.goal:
            self.path = self.find_awesome_path()
        else:
            if len(self.path) > 2:
                if point_dist(self.path[len(self.path)-2],obs.loc) <= self.settings.tilesize/2:
                    self.path.pop(len(self.path)-2)
        path = self.path
        if path:
            dx = path[len(path)-2][0] - obs.loc[0]
            dy = path[len(path)-2][1] - obs.loc[1]
            turn = angle_fix(math.atan2(dy, dx) - obs.angle)
            reverse_turn = angle_fix(math.atan2(-dy, -dx) - obs.angle)
            speed = (dx**2 + dy**2)**0.5
            if abs(reverse_turn) < abs(turn):
                turn = reverse_turn
                speed *= -1.0
            if abs(turn) >= self.settings.max_turn:
                if self.speed is not None:
                    speed = self.speed * 0.1
                else:
                    speed = 0            
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
        self.previous_goal = self.goal
        # check if goal is reached
        if self.goal is not None and point_dist(self.goal, obs.loc) < self.settings.tilesize:
            self.goal = None
        # Walk to random CP
        if self.goal is None and self.id == 0:
            self.goal = self.states[random.randint(0,len(self.states)-1)]
        if self.id == 0:
            drive = self.drive_tank()
        else:
            return (0,0,0)

        return (drive[0],drive[1],0)
        
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

        if self.goal is not None:
            pygame.draw.line(surface,(255,0,0),self.observation.loc, self.goal)
        
    def finalize(self, interrupted=False):
        """ This function is called after the game ends, 
            either due to time/score limits, or due to an
            interrupt (CTRL+C) by the user. Use it to
            store any learned variables and write logs/reports.
        """
        print "The end..."

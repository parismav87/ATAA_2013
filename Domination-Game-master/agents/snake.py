import itertools as it
import cPickle as pickle

FIELD = """w w w w w w w w w w w w w w w w w w w w w w w w w w w w w w w
w _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ w
w _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ w
w _ _ _ _ _ _ _ _ _ _ _ _ _ S _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ w
w _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ w
w _ _ _ _ _ _ _ W w w w w w w w w w w w w w W _ _ _ _ _ _ _ w
w _ _ _ W _ _ _ w _ _ _ _ _ _ _ _ _ _ S _ _ _ _ _ _ W _ _ _ w
w _ _ _ w _ _ _ w _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ w _ _ _ w
w S _ _ w _ _ _ W _ _ _ _ W w w w W _ _ _ _ W _ _ _ w _ _ S w
w _ _ _ w _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ w _ _ _ w _ _ _ w
w _ _ _ W _ _ _ _ _ _ S _ _ _ _ _ _ _ _ _ _ w _ _ _ W _ _ _ w
w _ _ _ _ _ _ _ W w w w w w w w w w w w w w W _ _ _ _ _ _ _ w
w _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ w
w _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ S _ _ _ _ _ _ _ _ _ _ _ _ _ w
w _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ w
w _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ w
w w w w w w w w w w w w w w w w w w w w w w w w w w w w w w w"""


BLACK_MAMBA = """
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:@@@:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@++@:;;;@'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@,@@@,#@@@@@#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#'@@,'@:#@@@#,@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'@+#:@@@@@@@@++@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'@:#,@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@,@+,#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@;@,;:#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'@#+':+@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#'@,@;@+:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#@@:+@;;;@:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@;#@;@,,@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@;@'@#,@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:;:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:@#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.';'@@@@@@@;@'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@+@@@@'@@@@@@'@+;@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'@;;'@@#@@@@,@+@'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@;++@,,@@'###@@:@:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#:+@:'@@;@@+;@,@#''#':@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@++,::##@+'@;#@@:@@@@@#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@,@#,'#:@;#@@@@+:+,@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@;@@@#@@@.+:@@@':,@,'#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:+@@@@#'+#:@@@@@;@@;+@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@+'',+@@##':';,,@@@'@:+@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@::,,;#@@@@@@#::::',@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@':::+@@@@@@@@@@@@@@@@@@@@@@@@@@@#@@@@@@@@@@+@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@;:::::,@@@@@@@@@@@@@@@@@@@@@@@+::@@@@@@@@#:,#@@@@@@@@@@@@@@@@@@@@@@@@@@#+,:@@@@@@@@@@
@@@@@@@@@@+,,,::,:#@@@,:,@@@@@@@@@@@@@@@,:#@@@@@@@@:::+@@@,:,+@@@@@@@@@@@@@@@@@@@@,,#@@@@@@@@@@
@@@@@@@@@@@::@@@:::#@@,:,@@@@@@@@@@@@@@@::@@,@@@@@@:::+@@#:::'@@@@@@@@@@@@@@@@@@@#::@@@@@@@@@@@
@@@@@@@@@@@:#@@::::@@':,;@@@#@@@@@#@@@@':,@;#@@@@@@::::@@,:::#@@@##@@@@@@@@@@@@@@,:,@@@@@#@#@@@
@@@@@@@@@@#:@#::::,@@,:,@@@,,,@@@@:'@@@,,#+,@@@@@@#,:,:@:::::@@@,::#@@@:'@@@@@@@@::#@@@@,,:@@@@
@@@@@@@@@@::,:::,:@#@::,@#;,:::@#,:,,@@::@:#@@@@@@',::,,:@:,:@@+::::@@,:#::#,,;@::,@@@@:::,.@@@
@@@@@@@@@@,:::::'#@@@,:+@@,#:,:@;,::,@#::,,@@@@@@@:,,:::;#:::@@,@::,@@::'::::,,#,::#:@@:#:::@@@
@@@@@@@@@@:::,:::::@'::@@,@:::'@,,:#'@::,:@@@@@@@@:;+:::@:::,@;#,:::@@,,:,,,::,@::#,,@,@:::'@@@
@@@@@@@@@@:'@#@@@:,'+:,@@,,,,:+@::#@@@:::::#@#@@@@,+@:;#@,::;@::::,;@#,,#:,+:,:@::@,;@:,:,:+@@@
@@@@@@@@@@,##,;,::'@#::@@::+#,'@:,@',#,:,::,@@@@@@,#@@@@@::,@@::'@::@+:,@:'#,,#@,:',@@::+#:'@@@
@@@@@@@@@@;@:,,:#@@@@:,@@,@#@::@',:,@@:'#,::#@@@@@,#@@@@#::@@@,@@@,,@+:@@@@@,@@@@::;@@,@@@,:@@@
@@@@@@@@@@@@@@@@@@@@@+,+:@@@@@#@@##@@@,@@@@@@#@@@@,@@@@@::@@@@@@@@@@@#;@@@@@@@@@@+,@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@;@@@@@@@@#@@@@@@@@@@@@@@@@@#@@@@@'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
"""

class Node(object):
    def __init__(self):
        self.data = None
        self.childs = None
        self.sumDistance = 0.0
        self.sumTurn = 0.0
        self.orientation = 0.0
        self.terminal = False
        self.parent = None

class Opponent(object):
    def __init__(self):
        self.loc = None
        self.angle = None
        self.id = None
        self.vel = None


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
        # attributes original
        self.id = id
        self.team = team
        self.mesh = nav_mesh
        self.grid = field_grid
        self.settings = settings
        self.callsign = '%s-%d'% (('BLU' if team == TEAM_BLUE else 'RED'), id)
        self.blobpath = "agents/snake_"+self.callsign

        # Monte Carlo attributes
        self.saveTrajectory = True
        self.Trajectory = list()

        # attributes for the map parsing
        self.map_width = 0
        self.map_height = 0
        self.states = None
        self.map = self.create_map()
        self.path_points = None
        self.find_path_state_points()
        self.walls = self.find_walls()

        # attributes for the states
        self.goal = self.states[4]
        self.currentState = None
        self.currentTeam = None
        self.previousState = None
        self.dead = False
        self.previousTeam = None
        self.previousAction = None
        self.currentCPS = (0,0)
        self.previousCPS = (0,0)
        self.currentAMMO = False
        self.previousAMMO = False
        self.reward = None

        # attributes for q learning
        self.qValid = False 

        # attributes for the shooting
        self.warMode = False
        self.foes = None

        # attributes for the driving
        self.speed = None
        self.path = None
        self.reverseMode = True
        
        # Recommended way to share variables between agents.
        if id == 0:
            self.all_agents = self.__class__.all_agents = []
        self.all_agents.append(self)
          
        # value table
        if self.id == 0:
            if os.path.isfile(self.blobpath):
                file = open(self.blobpath, "r")
                self.__class__.q = pickle.load(file)
                file.close()
            else:
                self.__class__.q = self.createQTable()

    def createQTable(self):
        Qtable = dict()
        n_of_agents = 3 
        transitions = it.permutations(self.states, 2)
        state_space = it.chain(self.states, transitions)
        for p in state_space:
            Qtable[p] = dict()
            ammo = [True, False]
            for am in ammo:
                Qtable[p][am] = dict()
                cps_con = [-1, 0, 1]
                cps = it.product(cps_con,cps_con, repeat = 1)
                for c in cps:
                    Qtable[p][am][c] = dict()
                    for a in self.states:
                        Qtable[p][am][c][a] = 20.0
        return Qtable

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
        self.obs = observation
        self.selected = observation.selected
        if observation.selected:
            print observation

    def shoot(self):
        # Shoot enemies
        shoot = False
        if (self.obs.ammo > 0 and 
            self.obs.foes and 
            point_dist(self.obs.foes[0][0:2], self.obs.loc) < self.settings.max_range and
            not line_intersects_grid(self.obs.loc, self.obs.foes[0][0:2], self.grid, self.settings.tilesize)):
            self.goal = self.obs.foes[0][0:2]
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
        if self.obs.cps[0][2] == 1:
            controlPoint1 += 1
        if self.obs.cps[0][2] == 0:
            controlPoint1 -= 1
        if self.obs.cps[1][2] == 1:
            controlPoint2 += 1
        if self.obs.cps[1][2] == 0:
            controlPoint2 -= 1
        self.currentCPS = (controlPoint1,controlPoint2)

    def find_awesome_path(self):
        if not line_intersects_grid(self.obs.loc, self.goal, self.grid, self.settings.tilesize):
            return [self.goal, self.obs.loc]
        else:
            temp_points = self.path_points
            # create the root element of the tree
            root = Node()
            root.data = self.obs.loc
            root.terminal = False
            root.parent = None
            root.orientation = self.obs.angle
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

    def check_if_dead(self):
        if self.obs.respawn_in == 10:
            self.dead = True

    def drive_tank(self):
        path = find_path(self.obs.loc, self.goal, self.mesh, self.grid, self.settings.tilesize)
        self.reverseMode = (self.obs.ammo == 0)
        if path:
            dx = path[0][0] - self.obs.loc[0]
            dy = path[0][1] - self.obs.loc[1]
            turn = angle_fix(math.atan2(dy, dx) - self.obs.angle)
            reverse_turn = angle_fix(math.atan2(-dy, -dx) - self.obs.angle)
            speed = (dx**2 + dy**2)**0.5
            if self.reverseMode:
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
        self.driveShoot = (turn, speed, False)

    def checkOpponents(self):
        oppDict = dict()
        oppList = list()
        for agent in self.all_agents:
            for opponent in agent.obs.foes:
                if opponent[0:2] not in oppDict:
                    temp = Opponent()
                    temp.loc = opponent[0:2]
                    temp.id = len(oppList)
                    temp.angle = opponent[2]
                    oppDict[temp.loc] = temp
                    oppList.append(temp)
        if self.foes is None and len(oppList) > 0:
            self.foes = oppList
        elif self.foes is not None and len(oppList) > 0:
            newOppList = []
            for prev_foe in self.foes:
                if len(oppList) > 0:
                    for i in range(len(oppList)-1):
                        new_foe = oppList[i]
                        dx = new_foe.loc[0] - prev_foe.loc[0]
                        dy = new_foe.loc[1] - prev_foe.loc[1]
                        turn = abs(angle_fix(math.atan2(dy, dx) - prev_foe.angle))
                        velocity = (dx**2 + dy**2)**0.5
                        if abs(turn) < self.settings.max_turn and velocity < 40.0:
                            oppList.pop(i)
                            prev_foe.loc = new_foe.loc
                            prev_foe.angle = new_foe.angle
                            prev_foe.vel = velocity
                            newOppList.append(prev_foe)
            if len(oppList) > 0:
                for opp in oppList:
                    newOppList.append(opp)
            self.foes = newOppList                        
        else:
            self.foes = oppList

    def checkWarMode(self):
        war = False
        if len(self.foes) > 0:
            for foe in self.foes:
                if point_dist(foe.loc, self.obs.loc) < 1.5 * self.settings.max_range:
                    war = True
        self.warMode = war

    def shoot(self):
        if self.obs.ammo > 0:
            #team blue starting angle is pi and red is 0. so that means, the angle is calculated facing to the right (normal stuff)
            for foe in self.obs.foes:
                dx = foe[0] - self.obs.loc[0]
                dy = foe[1] - self.obs.loc[1]
                angle = angle_fix(math.atan2(dy, dx))
                da = (self.obs.angle-angle)
                dist = (dx**2 + dy**2)**0.5
                if math.degrees(abs(da))<= math.degrees(math.atan2(45,dist)) and dist<self.settings.max_range and not line_intersects_grid(self.obs.loc, foe[0:2], self.grid, self.settings.tilesize):
                    friendly_fire = False
                    for agent in self.all_agents:
                        if agent.id != self.id:
                            friendly_dx = agent.obs.loc[0] - self.obs.loc[0]
                            friendly_dy = agent.obs.loc[1] - self.obs.loc[1]
                            friendly_angle = angle_fix(math.atan2(friendly_dy, friendly_dx))
                            friendly_da = (self.obs.angle-friendly_angle)
                            friendly_dist = (friendly_dx**2 + friendly_dy**2)**0.5
                            if math.degrees(abs(friendly_da)) <= math.degrees(math.atan2(45,friendly_dist)) and friendly_dist < dist:
                                friendly_fire = True
                    if not friendly_fire:
                        self.driveShoot = (da*(self.obs.angle/abs((self.obs.angle)+0.001)),0,True)

    def state_of_team(self):
        # team = ()
        # team += (self.currentState,)
        # for agent in self.all_agents:
        #     if agent.id != self.id:
        #         team += (agent.goal,)
        # self.currentTeam =  team
        self.currentTeam = self.currentState

    def eGreedy(self, epsilon):
        if random.random() < epsilon :
            return self.states[random.randint(0,len(self.states)-1)]
        else:
            bestMoves = []
            bestValue = -float('Inf')
            for move, value in self.__class__.q[self.currentTeam][self.currentAMMO][self.currentCPS].iteritems():
                if value > bestValue:
                    bestMoves = []
                    bestMoves.append(move)
                    bestValue = value
                if value == bestValue:
                    bestMoves.append(move)
            r = math.floor(random.random() * len(bestMoves))
            return bestMoves[int(r)]

    def check_state(self):
        if self.obs.step == 1:
            self.currentState = self.states[5]
        else:
            if point_dist(self.goal, self.obs.loc) <= self.settings.tilesize:
                self.currentState = self.goal
                self.goal = None
            else:
                if type(self.currentState[0]) is type(tuple()):
                    if self.equal(self.goal, self.currentState[0]):
                        self.currentState = (self.currentState[1], self.goal)
                    else:
                        self.currentState = (self.currentState[0], self.goal)
                else:
                    self.currentState = (self.currentState, self.goal)
        if type(self.currentState[0]) is type(tuple()):
            if self.equal(self.currentState[0], self.currentState[1]):
                self.currentState = self.currentState[0]
        return

    def stateMaxValue(self):
        bestValue = -float('Inf')
        for move, value in self.__class__.q[self.currentTeam][self.currentAMMO][self.currentCPS].iteritems():
            if value > bestValue:
                bestValue = value
        return bestValue

    def check_reward(self):
        reward = 0.0
        for i in range(len(self.currentCPS)):
            reward += (self.currentCPS[i] - self.previousCPS[i]) * 10.0
        self.reward = reward

    def choose_action(self, type, e, t):
        if type == "egreedy":
            self.goal = self.states[random.randint(0,len(self.states)-1)]
            if self.obs.step > 1:
                self.goal = self.eGreedy(0.1)
        elif type == "random":
            if self.goal is None:
                self.goal = self.states[random.randint(0,len(self.states)-1)]
            else:
                if random.random() < e:
                    self.goal = self.states[random.randint(0,len(self.states)-1)]
        else:
            pass

    def learning(self, algorithm, alpha, gamma):
        if algorithm == "qlearning":
            self.check_validity_q()
            if self.qValid:
                self.qLearning(alpha, gamma)
        elif algorithm == "sarsa":
            pass
        elif algorithm == "wolf":
            pass

    def check_validity_q(self):
        valid = True
        if type(self.previousTeam) == type(tuple()):
            for a in self.previousTeam:
                if a is None:
                    valid = False
        if self.previousAction is None:
            valid = False
        self.qValid = valid


    def qLearning(self, alpha, gamma):
        pass
        self.__class__.q[self.previousTeam][self.previousAMMO][self.previousCPS][self.previousAction] = \
        self.__class__.q[self.previousTeam][self.previousAMMO][self.previousCPS][self.previousAction] \
        + alpha * ( self.reward + gamma * self.stateMaxValue() - self.__class__.q[self.previousTeam][self.previousAMMO][self.previousCPS][self.previousAction])

    def checkAMMO(self):
        pass
        self.currentAMMO = (self.obs.ammo > 0)

    def updatePreviousState(self):
        self.previousAMMO = self.currentAMMO
        self.previousCPS = self.currentCPS
        self.previousTeam = self.currentTeam
        self.previousState = self.currentState
        self.previousAction = self.goal
        return 

    def action(self):
        """ This function is called every step and should
            return a tuple in the form: (turn, speed, shoot)
        """
        self.checkOpponents()
        self.checkWarMode()
        self.check_if_dead()
        self.check_cps()
        self.checkAMMO()
        self.check_reward()
        self.check_state()
        self.state_of_team()
        self.choose_action("egreedy", 0.1, None)
        self.learning("qlearning", 0.7, 0.7)
        self.updatePreviousState()
        self.drive_tank()
        self.shoot()
        return self.driveShoot
        
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

        if self.id == 0:
            if self.foes is not None:
                for opponent in self.foes:
                    if opponent.id == 0:
                        pygame.draw.circle(surface, (255,0,0), opponent.loc, 15, 2)
                    if opponent.id == 1:
                        pygame.draw.circle(surface, (0,255,0), opponent.loc, 15, 2)
                    if opponent.id == 2:
                        pygame.draw.circle(surface, (0,0,255), opponent.loc, 15, 2)
        
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
                    file = open(self.blobpath, "w")
                    pickle.dump(self.__class__.q, file)
                    file.close()
                except:
                    # We can't write to the blob, this is normal on AppEngine since
                    # we don't have filesystem access there.        
                    print "Agent %s can't write blob." % self.callsign
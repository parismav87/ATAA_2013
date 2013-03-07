import math
import copy
from random import choice
from libs.astar import astar

# Map with extra points of interest for the mesh
map_grid = """
w w w w w w w w w w w w w w w w w w w w w w w w w w w w w
w _ _ _ _ _ _ # _ _ # _ _ _ _ _ _ _ _ _ _ # _ _ _ _ _ _ w
w _ _ _ _ _ _ _ _ _ o # o _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ w
w _ _ _ _ _ _ _ _ _ _ w _ C _ _ _ _ _ _ _ _ _ _ _ _ _ _ w
w _ _ _ # _ o _ o # _ w _ _ _ _ _ _ _ _ _ _ o _ # _ _ _ w
w _ o _ o _ _ w _ _ _ w w w w w w w w w w w _ _ o _ o _ w
w _ _ w _ _ _ w _ _ o # _ # # # _ # _ _ _ _ o _ _ w _ _ w
w R _ w _ _ _ w _ _ _ _ _ _ _ _ _ _ _ _ o _ o _ _ w _ B w
w R _ w _ _ _ w _ A _ _ w w w w w _ _ A _ w _ _ _ w _ B w
w R _ w _ _ o _ o _ _ _ _ _ _ _ _ _ _ _ _ w _ _ _ w _ B w
w _ _ w _ _ o _ _ _ _ # _ # # # _ # o _ _ w _ _ _ w _ _ w
w _ o _ o _ _ w w w w w w w w w w w _ _ _ w _ _ o _ o _ w
w _ _ _ # _ o _ _ _ _ _ _ _ _ _ _ w _ # o _ o _ # _ _ _ w
w _ _ _ _ _ _ _ _ _ _ _ _ _ _ C _ w _ _ _ _ _ _ _ _ _ _ w
w _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ o # o _ _ _ _ _ _ _ _ _ w
w _ _ _ _ _ _ # _ _ _ _ _ _ _ _ _ _ # _ _ # _ _ _ _ _ _ w
w w w w w w w w w w w w w w w w w w w w w w w w w w w w w
"""


def locs_from_map(map_grid, sig='#', tilesize=16):
    """Yields all x, y coordinates of a certain character on the map.
    """
    for x, line in enumerate(map_grid.split('\n')[1:-1]):
        for y, char in enumerate(line[::2]):
            if char == sig:
                yield int(tilesize * (y + .5)), int(tilesize * (x + .5))


def discretize(y, x, tilesize=16):
    """Return the discretised location of a position (to the middle of the
    corresponding tile).
    """
    return (int(tilesize * (int(y / tilesize) + .5)),
            int(tilesize * (int(x / tilesize) + .5)))


class SharedKnowledge():
    """ Decomposes observations by agents to create a global world model:
        - Ammo_info
        - Spawn_info
        - Controlpoints
        - Foe-locations
        - Agent-locations
        - Ammo per agent
        - Visible (killable) foes per agent
    """

    # Gamestates
    INIT = -2
    LOSING = -1
    EVEN = 0
    WINNING = 1

    NUM_AGENTS = 3

    # Dynamic world variables
    ammo_info = {}         # Spawntime indexed by ammo_loc
    spawn_info = []        # Spawntime indexed by agent_id
    cps = []               # Controlpoint (x,y,state)
    foes = []              # Foes by location (x,y,r)
    foe_respawns = []      # Respawn times of foes

    # Agent variables
    ammos = []             # Ammo by agentid
    visible_targets = []   # Seen foes by agentid

    def __init__(self, mesh, all_agents, team, settings):
        self.all_agents = all_agents
        self.team = team
        self.settings = settings

        self.mesh = self.init_mesh(mesh)
        self.state = self.INIT

        # Add interesting nodes and set initial info
        for node in locs_from_map(map_grid, '#'):
            self.add_to_mesh(mesh, node, 0)
        for ammo in [a for a in locs_from_map(map_grid, 'A')]:
            self.ammo_info[ammo] = 0
        for cp in [c for c in locs_from_map(map_grid, 'C')]:
            self.cps.append(cp + (0,))
        self.spawn_info = [0] * self.NUM_AGENTS
        self.ammos = [0] * self.NUM_AGENTS
        self.visible_targets = [None] * self.NUM_AGENTS

        self.foe_respawns = [0] * self.NUM_AGENTS

        # Initial orders are empty
        self.orders = {0: None, 1: None, 2: None}

    def update_knowledge(self):
        """ All agent observations are present! Use to find:
            - current cp and their status
            - visible ammopacks
            - all foes in range
            - visible foes per agent
        """

        # Local vars for efficiency
        visible_targets = list()
        spawn_info = list()
        ammos = list()
        ammopacks = set()
        foes = set()

        for agent in self.all_agents:
            obs = agent.observation

            # Seen foes, indexed by agentid, values are dicts:
            # {foe : angle_needed_for_kill}
            visible_targets.append(agent.visible_targets())

            # Present ammopacks
            ammopacks |= set([x[:2] for x in
                              filter(lambda x: x[2] == "Ammo", obs.objects)])

            # If we see ammo, set timer to 0
            for ammopack in ammopacks:
                self.ammo_info[ammopack] = 0

            # Present foes (location only)
            foes |= set(obs.foes)

            # Ammo per agent
            ammos.append(obs.ammo)

            # Spawn_time per agent
            spawn_info.append(obs.respawn_in)

        self.visible_targets = visible_targets
        self.spawn_info = spawn_info
        self.ammos = ammos
        self.ammopacks = ammopacks
        self.foes = foes

        # Dynamic world variable cps is the same for each agent
        cps = self.all_agents[0].observation.cps
        game_score = self.all_agents[0].observation.score
        cps_foe = len([c for c in cps if c[2] != self.team and c[2] != 2])
        cps_friend = len([c for c in cps if c[2] == self.team])
        cps_even = len(cps) - cps_foe - cps_friend
        self.cps = cps

        if cps_even == len(cps):
            if max(self.spawn_info) == -1 and game_score == (50, 50):
                self.state = self.INIT
            else:
                self.state = self.EVEN
        elif cps_foe > cps_friend:
            self.state = self.LOSING
        elif cps_foe == cps_friend:
            self.state = self.EVEN
        elif cps_foe < cps_friend:
            self.state = self.WINNING

        # Update ammo timers
        for ammo, count in self.ammo_info.iteritems():
            self.ammo_info[ammo] = max(0, self.ammo_info[ammo] - 1)
            if count == 0 and not ammo in ammopacks:
                for a in self.all_agents:
                    if point_dist(a.loc, ammo) < self.settings.max_see:
                        # assume it's gone
                        self.ammo_info[ammo] = self.settings.ammo_rate

                # TODO predict if opponent took it

        # Update enemy spawn times
        for i,time in enumerate(self.foe_respawns):
            if time > 0:
                self.foe_respawns[i] -= 1

    def reward(self):
        return self.state

    def foe_killed(self):
        for i,time in enumerate(self.foe_respawns):
            if time == 0:
                self.foe_respawns[i] = self.settings.spawn_time
                break

    def init_mesh(self, mesh):
        """ Mesh is a dict of dicts mesh[(x1,y1)][(x2,y2)] = nr_of_turns

            NOTE nr_of_turns does not include turning of the agent
        """
        # TODO add custom points using Haar features?

        # Nodes are given equal cost if in same movement range
        for node1 in mesh:
            for node2 in mesh[node1]:
                # Get the old movement cost
                cost = math.ceil(mesh[node1][node2] /
                                 float(self.settings.max_speed))
                mesh[node1][node2] = cost * self.settings.max_speed

        return mesh

    def add_to_mesh(self, mesh, node, bonus):
        """ Add one node to the mesh, connect to every possible
            present node, give it bonus (so agents have an incentive
            to reach it).

            NOTE overrides previous values completely.
        """
        tilesize = self.settings.tilesize
        max_speed = self.settings.max_speed
        grid = self.all_agents[0].grid

        # Add nodes!
        mesh[node] = dict([(n, math.ceil(point_dist(node, n) /
                                         float(max_speed)) *
                            max_speed - bonus) for n in mesh if not
                          line_intersects_grid(node, n, grid, tilesize)])

        return mesh

    def get_ammo_time(self, ammo_loc):
        """ Returns the respawn time for the given ammo location. Note
            that this is based on knowledge of this team only, so may be
            inaccurate.
        """
        return self.ammo_info[ammo_loc]

    def set_ammo_time(self, ammo_loc, time):
        """ Sets the respawn time for the given ammo location to the
            given amount.
        """
        self.ammo_info[ammo_loc] = self.settings.ammo_rate


class Brigadier():
    """ Brigadier commands all agents on a meta-level.
        1 Plan:      Choose order per agent
        2. Action:   Set a goal (x,y) based on the order
    """

    DEFENSIVE = 0
    AGGRESSIVE = 1
    HOGGING = 2

    def __init__(self, shared_knowledge):
        self.shared_knowledge = shared_knowledge

    def __del__(self):
        pass

    def strategize(self):
        self.plan(self.shared_knowledge.state,
                  self.shared_knowledge.ammo_info,
                  self.shared_knowledge.spawn_info)
        self.action()

    def plan(self, gamestate, ammo_info, spawn_info):
        """ Plan meta-actions for all agents. Currently hardcoded
            initial state.
        """
        orders = self.shared_knowledge.orders
        all_agents = self.shared_knowledge.all_agents
        cps = self.shared_knowledge.cps
        team = self.shared_knowledge.team
        visible_targets = self.shared_knowledge.visible_targets
        ammos = self.shared_knowledge.ammos
        foes = self.shared_knowledge.foes

        # used functions
        cp_attack = self.cp_attack
        get_ammo = self.get_ammo
        kill_foe = self.kill_foe
        wait = self.wait

        if gamestate == self.shared_knowledge.INIT:
            if team == TEAM_BLUE:
                orders[0] = (cp_attack, {'cp': cps[0]})
                orders[2] = (cp_attack, {'cp': cps[1]})
                orders[1] = (get_ammo, {'ammo_info': ammo_info})
            elif team == TEAM_RED:
                orders[0] = (cp_attack, {'cp': cps[0]})
                orders[2] = (cp_attack, {'cp': cps[1]})
                orders[1] = (get_ammo, {'ammo_info': ammo_info})

        # Go for controlpoints with the closest agent preferably
        cps_to_get = [cp for cp in cps if cp[2] != team]
        cps_to_defend = [cp for cp in cps if cp[2] == team]
        ammos = self.shared_knowledge.ammos
        agent_ids = [a.id for a in all_agents]
        dead_foes = len([f for f in self.shared_knowledge.foe_respawns if f > 0])

        # Update goals
        for id, (order, goal) in orders.iteritems():
            if order == get_ammo:
                orders[id] = (get_ammo, {'ammo_info': ammo_info})
                
                best_ammo = self.get_best_ammo_loc(all_agents[id], self.shared_knowledge.ammo_info)
                switched = False
                if dead_foes > 0 and all_agents[id].ammo > 0:
                    least_ammo_guy = id
                    least_ammo = all_agents[id].ammo
                    for other_agent in all_agents:
                        other_id = other_agent.id
                        if other_agent.ammo < least_ammo and spawn_info[other_id] == -1:
                            least_ammo_guy = other_id
                            least_ammo = other_agent.ammo

                    if least_ammo_guy != id:
                        self.switch_roles(id, least_ammo_guy)
                        switched = True


                # special case: Even and we hogged enough ammo
                if not switched and (all_agents[id].ammo > 2 or spawn_info[id] > -1):
                    #self.switch_roles(id, choice([a.id for a in all_agents
                    #                              if a.id != id]))
                    closest = self.closest_to_point(best_ammo)
                    if id == closest:
                        closest = choice([a.id for a in all_agents if a.id != id]) 
                    self.switch_roles(id, closest)

            # And be sure to always attack targets
            if visible_targets[id]:
                foe = visible_targets[id].keys()[0]
                turn, speed = visible_targets[id].values()[0]
                visible_targets[id] = (foe, turn, speed)


            agent = all_agents[id]
            # Defending agents must camp at all times
            if order == self.cp_defend:
                # If we were defending a cp and that cp has been recaptured, attack again!
                if goal['cp'][:2] in cps_to_get:
                    orders[id] = (self.cp_attack, {'cp': goal['cp']})
                if not agent.ammo:
                    # Attack original cp if out of ammo
                    orders[id] = (self.cp_attack, {'cp': goal['cp']})

            elif agent.ammo and agent.goal_reached():
                if order == self.cp_attack:
                    # If we were attacking a cp and succeeded, go defend
                    spot = self.closest_object(agent.loc, agent.campspots)
                    if point_dist(spot[:2], agent.loc[:2]) < \
                            agent.settings.max_range:
                        orders[id] = (self.cp_defend, {'spot': spot, 
                                                            'cp': goal['cp']})

    def switch_roles(self, id1, id2):
        """ Function that switches two agents' orders given their id.
        """
        orders = self.shared_knowledge.orders
        temp = orders[id1]
        orders[id1] = orders[id2]
        orders[id2] = temp

    def action(self):
        """ Based on the order, set the goal for each agent.
        """
        for agent in self.shared_knowledge.all_agents:
            # Execute the found command
            (command, kwargs) = self.shared_knowledge.orders[agent.id]
            command(agent, **kwargs)

    ### META-ACTION FUNCTIONS ###
    def wait(self, agent, arg=None):
        agent.goal = agent.loc

    def kill_foe(self, agent, **kwargs):
        """ Kill a given foe or the closest foe.

            Should only be called when agent has ammo.
        """
        foe = kwargs['foe'] if 'foe' in kwargs else self.closest_foe(agent.loc)
        if foe:
            agent.goal = foe
        else:
            self.wait(agent)

    def cp_attack(self, agent, **kwargs):
        """ Attack the given or closest cp, regardless of ammo.
        """
        cp = kwargs['cp'] if 'cp' in kwargs else self.closest_cp(agent.loc)
        agent.goal = cp[:2]
 
    def cp_defend(self, agent, **kwargs):
        spot = kwargs['spot'] if 'spot' in kwargs else None
        if spot:
            agent.goal = spot

    def get_ammo(self, agent, **kwargs):
        """ Get given ammo, if no ammo found, goto best ammopoint
        """
        ammo_info = kwargs['ammo_info']

        # walk to the best ammospot
        best_ammo = self.get_best_ammo_loc(agent, ammo_info)
        if best_ammo:
            agent.goal = best_ammo
        else:
            self.cp_attack(agent)

    ### BESTSOFAR FUNCTIONS ###
    def get_best_ammo_loc(self, agent, ammo_info):
        """ Returns the best place to go to for ammo plus time until it
            is spawned:
            - if two locations have ammo, nearest one is returned
            - if no locations have ammo, shortest spawn time is returned
        """
        loc = agent.loc
        best_time = self.shared_knowledge.settings.ammo_rate
        best_ammo = None
        best_dist = 1e5
        # TODO Use astar pathplanning instead
        for ammo, spawn_time in ammo_info.iteritems():
            _, d = agent.find_optimal_path(ammo)
            turns_needed = int(d / self.shared_knowledge.settings.max_speed)

            time_to_get_ammo = max(spawn_time, turns_needed)

            if time_to_get_ammo < best_time:
                best_ammo = ammo
                best_time = time_to_get_ammo
                best_dist = d
            elif spawn_time == best_time:
                if d < best_dist:
                    best_ammo = ammo
                    best_dist = d
        return best_ammo  # TODO return besttime?

    def closest_object(self, loc, objectlist):
        """ Get the closest objects from a given list of objects
            using a best-so-far method.
        """
        best_dist = 1000
        best_object = None
        for o in objectlist:
            dist = real_dist(loc, o[:2])
            if dist < best_dist:
                best_dist = dist
                best_object = o
        return best_object

    def closest_foe(self, loc, foelist=None):
        """ Get the closest foe from a given list or all foes.
        """
        foelist = foelist if foelist else self.shared_knowledge.foes
        return self.closest_object(loc, foelist)

    def closest_ammopack(self, loc, ammopacklist=None):
        """ Get the closest ammo from a given list or all ammo.
        """
        ammopacklist = ammopacklist if ammopacklist else \
            self.shared_knowledge.ammopacks
        return self.closest_object(loc, ammopacklist)

    def closest_cp(self, loc, cplist=None):
        """ Get the closest cp from a given list or all cp.
        """
        cplist = cplist if cplist else self.shared_knowledge.cps
        return self.closest_object(loc, cplist)

    def closest_to_point(self, point):
        """ Determine which agent is closest to a given point. Ammo,
            which is False by default, specifies whether this close
            agent should have ammo.
        """
        best_dist = 1000
        best_id = None
        for agent in self.shared_knowledge.all_agents:
            dist = real_dist(agent.loc[:2], point[:2])
            if dist < best_dist:
                dist = best_dist
                best_id = agent.id
        return best_id

    def __str__(self):
        """ Tostring method prints all items of the brigadier object.
        """
        items = sorted(self.__dict__.items())
        maxlen = max(len(k) for k, v in items)
        return "== BRIGADIER ==\n" + "\n".join(('%s : %r' %
                                                (k.ljust(maxlen), v))
                                               for (k, v) in items)


# AUXILIARY
def real_dist(a, b):
    """ Should compute the real length of the path. For now,
        equals point_dist.
    """
    return point_dist(a, b)


class Agent(object):
    NAME = "SillyBot"

    def __init__(self, id, team, settings=None, field_rects=None,
                 field_grid=None, nav_mesh=None, blob=None, **kwargs):
        """ Each agent is initialized at the beginning of each game.
            The first agent (id==0) can use this to set up global variables.
            Note that the properties pertaining to the game field might not be
            given for each game.
        """
        self.id = id
        self.team = team
        self.grid = field_grid
        self.corners = get_corners(field_grid)
        self.campspots = [(24.0, 24.0, 0.7853981633974483), (440.0, 24.0, 2.356194490192345), (200.0, 72.0, -0.7853981633974483), (264.0, 200.0, 2.356194490192345), (24.0, 248.0, -0.7853981633974483), (440.0, 248.0, -2.356194490192345)]
        self.settings = settings
        self.goal = None
        self.callsign = '%s-%d' % (('BLU' if team == TEAM_BLUE else 'RED'), id)
        self.relocate = True

        # Read the binary blob, we're not using it though
        #if blob is not None:
        #    print "Agent %s received binary blob of %s" % (
        #       self.callsign, type(pickle.loads(blob.read())))
        #    # Reset the file so other agents can read it.
        #    blob.seek(0)

        # Recommended way to share variables between agents.
        if id == 0:
            self.all_agents = self.__class__.all_agents = [self]
            self.shared_knowledge = self.__class__.shared_knowledge =\
                SharedKnowledge(nav_mesh, self.all_agents, team, settings)
            self.brigadier = self.__class__.brigadier =\
                Brigadier(self.shared_knowledge)
        else:
            self.all_agents.append(self)

    def observe(self, observation):
        """ Each agent is passed an observation using this function,
            before being asked for an action. You can store either
            the observation object or its properties to use them
            to determine your action. Note that the observation object
            is modified in place.
        """
        self.observation = observation
        self.selected = observation.selected

        self.loc = self.observation.loc + (self.observation.angle,)
        self.ammo = self.observation.ammo
        self.shoot = False

        # Additional info on each observed foe for easy later use
        foes = {}
        for foe in observation.foes:
            rel_angle_to_foe = get_rel_angle(self.loc, foe)
            rel_angle_from_foe = get_rel_angle(foe, self.loc)
            point_dist_to_foe = point_dist(self.loc, foe[:2])
            path_to_foe = self.find_optimal_path(foe)
            # path to foe is not that computationally expensive!
            foes[foe] = (rel_angle_to_foe,
                         rel_angle_from_foe,
                         path_to_foe,
                         point_dist_to_foe)
        self.foes = foes

        #if observation.selected:
        #    print observation

        # All agent observations are present
        if self.id == len(self.all_agents) - 1:
            self.shared_knowledge.update_knowledge()
            self.brigadier.strategize()

    def action(self):
        """ This function is called every step and should
            return a tuple in the form: (turn, speed, shoot)
        """
        # Find the optimal path through the mesh
        path, _ = self.find_optimal_path()

        # Always go for targets!
        visible_targets = self.shared_knowledge.visible_targets[self.id]
        if self.ammo and visible_targets:

            foe, turn, speed = visible_targets

            # Adapt speed: cos(a) * dist_to_goal
            new_orientation = angle_fix(self.loc[2] + turn)
            newloc = self.loc[:2] + (new_orientation,)

            speed = 0  # (math.cos(angle_fix(get_rel_angle(newloc, foe))) *
            # min(point_dist(self.loc[:2], path[0][:2]),
            #     self.settings.max_speed)

            # And shoot the selected target
            shoot = True
            print 'Owned {0}.'.format(foe)
            self.shared_knowledge.foe_killed()
            return turn, speed, shoot

        if path:
            dx = path[0][0] - self.loc[0]
            dy = path[0][1] - self.loc[1]

            speed = (dx**2 + dy**2)**0.5

            turn = angle_fix(math.atan2(dy, dx) - self.loc[2])
            if abs(turn) > self.settings.max_turn + 0.15:
                speed = 0
                self.shoot = False

            if self.goal_reached():
                if len(self.goal) > 2:
                    turn = angle_fix(self.goal[2] - self.loc[2])
                elif self.foes:
                    foe = self.brigadier.closest_foe(self.loc)
                    #if not line_intersects_grid(self.loc[:2], foe[:2], self.grid,
                    #    self.settings.tilesize):
                    turn = angle_fix(get_rel_angle(self.loc, foe))
                elif self.team == TEAM_RED:
                    turn = angle_fix(-self.loc[2])
                else:
                    turn = angle_fix(math.pi - self.loc[2])
                speed = 0
        else:
            turn = 0
            speed = 0

        return (turn, speed, self.shoot)

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
            surface.fill((0, 0, 0, 0))
        # Selected agents draw their info
        if self.selected:
            if self.goal is not None:
                pygame.draw.line(surface, (0, 0, 0), self.observation.loc,
                                 self.goal[:2])

    def finalize(self, interrupted=False):
        """ This function is called after the game ends,
            either due to time/score limits, or due to an
            interrupt (CTRL+C) by the user. Use it to
            store any learned variables and write logs/reports.
        """
        pass

    def __str__(self):
        return "Agent " + self.id

    def find_optimal_path(self, goal=None):
        """ Pathplanning! Uses navmesh nodes as astar nodes, cost adjusted
            to match the real cost of the movement (including turns).
        """
        # Define current and goal location
        loc = self.loc
        start = self.loc[:2]
        goal = goal if goal else self.goal
        end = goal[:2]

        # For readability and perhaps even speed
        grid = self.grid
        tilesize = self.settings.tilesize
        max_speed = self.settings.max_speed
        max_turn = self.settings.max_turn

        # If there is a straight line, just return the end point
        if not line_intersects_grid(start, end, grid, tilesize):
            return [goal], 40

        # Copy mesh so we can add temp nodes
        mesh = copy.deepcopy(self.shared_knowledge.mesh)
        # Add temp nodes for start
        mesh[start] = dict([(n, point_dist(start, n)) for n in mesh if not
                            line_intersects_grid(start, n, grid, tilesize)])
        # Add temp nodes for end:
        if end not in mesh:
            endconns = [(n, point_dist(end, n)) for n in mesh if not
                        line_intersects_grid(end, n, grid, tilesize)]
            for n, dst in endconns:
                mesh[n][end] = dst

        # NOTE TO SELF:
        # We're currently faking that the rotated node is a neighbour
        # as well by implicitly representing the move to a rotated node
        # through extra cost
        neighbours = lambda n: [n2 + (get_angle(n, n2),)
                                for n2 in mesh[n[:2]].keys()]
        # cost is meshcost + number of steps needed for turn
        cost = lambda n1, n2: (mesh[n1[:2]][n2[:2]] +
                               abs(int(get_rel_angle(n1, n2) / max_turn))*40)
        # Goal disregards orientation
        goal = lambda n: n[:2] == end[:2]
        # Heuristic, Euclidean + orientation orientation into account?
        heuristic = lambda n: (((n[0]-end[0])**2 + (n[1]-end[1])**2) ** 0.5 +
                               abs(int(get_rel_angle(n, end) / max_turn)))
        nodes, length = astar(loc, neighbours, goal, 0, cost, heuristic)
        return nodes, length

    def visible_targets(self):
        """ Determine foes that can be hit in this turn.

            Return a dict indexed by foes, values are
            corresponding relative (speed, angle).
        """
        loc = self.loc
        obs = self.observation
        visible_targets = {}
        max_turn = self.settings.max_turn
        max_range = self.settings.max_range
        agent_radius = 7

        # Foes are possible targets if in range and in turnrange
        foes_in_range = [(foe, angles_plus_dist(loc, foe, agent_radius - 1,
                                                max_turn))
                         for foe, (a_to_foe, a_from_foe, path_to_foe,
                                   dist_to_foe) in self.foes.iteritems()
                         if dist_to_foe < max_range + agent_radius - 1 and
                         abs(a_to_foe) < max_turn + 0.1]

        # Stop if no foes in range found
        if not foes_in_range or not self.ammo:
            return visible_targets

        # Same goes for friends
        friends_in_range = [angles_plus_dist(loc, friend, agent_radius,
                                             max_turn)
                            for friend in obs.friends if
                            point_dist(loc[:2], friend[:2]) <
                            max_range + agent_radius and
                            abs(get_rel_angle(loc, friend)) < max_turn + 0.2]

        # Take corners into account as well,
        # [(x_wall, y_wall, type, dist), ...]
        wall_corners = corners_in_range(self.corners, loc)

        tilesize = self.settings.tilesize
        grid = self.grid

        # Check if foe-angles overlap with friend-angles or grid-angles
        for foe_loc, foe in foes_in_range:
            foe_a1, foe_a2, foe_dist = foe

            # Alter shot if an object is in front of the foe, or if another
            # foe is in front of it
            for obst in ([fr for fr in friends_in_range if fr[2] < foe_dist] +
                         [fo[1] for fo in foes_in_range if fo[1][2] <
                          foe_dist]):
                obst_a1, obst_a2, d = obst

                # Multiple cases for overlapping
                # - right-of-obstacle overlaps
                if foe_a1 < obst_a2 < foe_a2:
                    foe_a1 = obst_a2
                # - left-of-obstacle overlaps
                elif foe_a1 < obst_a1 < foe_a2:
                    foe_a2 = obst_a1
                # - entire overlap
                elif foe_a1 > obst_a1 and foe_a2 < obst_a2:
                    foe_a1 = None
                    foe_a2 = None

            # Alter shot depending on walls
            for wall in [w for w in wall_corners if w[3] < foe_dist]:
                # types wall:
                #
                #   0:  X _     1:  _ X
                #       _ _         _ _
                #
                #   2:  _ _     3:  _ _
                #       X _         _ X

                # Only one case: a wallcorner obstructs the view to
                # the foe. Enforced by saying radius = 0
                wall_corner1, wall_corner2 = angles_plus_dist(loc, wall[:2], 0,
                                                              max_turn)
                if foe_a1 < wall_corner1 < foe_a2:
                    # But distinguish between walltypes and orientation towards
                    # wall
                    # Hey I just saw walls
                    # and this is crazy
                    # but here's an if block
                    # TODO steven
                    walltype = obstacle[3]
                    # If the wall is left and below
                    if loc[0] > wall[0] and loc[1] > wall[1]:
                        if walltype == 0:
                            foe_a2 = obst_a1
                        elif walltype == 3:
                            foe_a1 = obst_a1
                    # elif wall is right and above
                    elif loc[0] < wall[0] and loc[1] < wall[1]:
                        if walltype == 0:
                            foe_a1 == obst_a1
                        elif walltype == 3:
                            foe_a2 = obst_a1
                    # elif wall is left and above
                    elif loc[0] > wall[0] and loc[1] < wall[1]:
                        if walltype == 1:
                            foe_a2 == obst_a1
                        elif walltype == 2:
                            foe_a1 = obst_a1
                    # elif wall is right and below
                    elif loc[0] < wall[0] and loc[1] < wall[1]:
                        if walltype == 1:
                            foe_a1 == obst_a1
                        elif walltype == 2:
                            foe_a2 = obst_a11

            # If angles are found, legit, differ sufficiently and do
            # not intersect with the grid
            if foe_a1 is not None and foe_a2 - foe_a1 > 0.025:
                target_angle = (foe_a1 + foe_a2) / 2.0
                # TODO Determine loc where foe is hit by shot

                # TEMPFIX
                # Use foe_dist (loc to mid of foe) to find a point
                # within the foe that is crossed by the line that
                # intersects the foe's circle.
                real_angle = angle_fix(loc[2] + target_angle)
                foe_hit = (loc[0] + math.cos(real_angle) * foe_dist,
                           loc[1] + math.sin(real_angle) * foe_dist,
                           real_angle)

                if not line_intersects_grid(loc[:2], foe_hit[:2], grid,
                                            tilesize):
                    visible_targets[foe_loc] = (target_angle, None)

        return visible_targets

    def can_shoot(self, foe):
        """ Check if possible to shoot a given enemy.
        """
        # Shoot enemies at all times
        return foe in self.visible_targets()

    def goal_reached(self, max_dist_from_goal=2):
        ''' Return if goal has been reached for this agent.

            An agent has reached its goal if it is sufficiently close.
        '''
        return self.goal is not None and (point_dist(self.goal, self.loc) <
                                          max_dist_from_goal)

    def alter_mesh(self, mesh):
        """ Mesh is a dict of dicts mesh[node1][node2] = cost.

            Add custom meshnodes for this agent, if necessary.
        """
        return mesh


# AUX FUNCTIONS
def line_intersection_with_circle((x1, y1, a1), (x2, y2), (cx, cy), r):
    """ Find the CLOSEST point of intersection for a given line and
        a circle described by its center coordinates and radius.

        Closest here means closest to x1,y1, from which the line is
        cast. x2,y2 is an auxiliary point needed to describe the
        line.

        Returns None if no intersection found.
    """
    max_next_loc = (x1 + math.cos(a1) * max_speed,
                    y1 + mat.sin(a1) * max_speed,
                    a1)

    dx = max_next_loc[0] - loc[0]
    dy = max_next_loc[1] - loc[1]
    dr = (dx**2 + dy**2)**0.5
    D = loc[0] * max_next_loc[1] - max_next_loc[0] * loc[1]
    # Discriminant indicates intersections:
    # discr < 0 -> no intersection
    # discr = 0 -> tangent (raaklijn)
    # discr > 1 -> intersection
    discr = (max_range+6)**2 * dr**2 - D**2
    sign = lambda x: (x < 0) * -1

    # if discr < 0, we're too far off
    if discr < 0:
        return (x, y)

    x_itsct = (D * dy + sign(dy) * dx * math.sqrt(discr)) / dr**2
    y_itsct = (-D * dx + abs(dy) * math.sqrt(discr)) / dr**2
    if discr == 0:
        return (x_itsct, y_itsct)

    x_itsct2 = (D * dy - sign(dy) * dx * math.sqrt(discr)) / dr**2
    y_itsct2 = (-D * dx - abs(dy) * math.sqrt(discr)) / dr**2

    if (point_dist((x1, y1), (x_itsct, y_itsct)) <
            point_dist((x1, y1), (x_itsct2, y_itsct2))):
        return (x_itsct, y_itsct)
    return (x_itsct2, y_itsct2)


def get_corners(walls, tilesize=16):
    """ Return indices of all wall corners and the type.
        types:

            0:  X _     1:  _ X
                _ _         _ _

            2:  _ _     3:  _ _
                X _         _ X

        format: (x, y, type)
    """
    corners = []
    for i in xrange(len(walls) - 1):
        for j in xrange(len(walls[0]) - 1):
            a = walls[i][j]
            b = walls[i + 1][j]
            c = walls[i][j + 1]
            d = walls[i + 1][j + 1]
            if a + b + c + d == 1:
                cornertype = b + 2 * c + 3 * d
                corners.append((tilesize * (i + 1),
                                tilesize * (j + 1), cornertype))
    return corners


def corners_in_range(corners, loc, rng=60):
    """ Get corner_x, corner_y, corner_type_, corner_dist for
        corners in specific range.
    """
    for corner in corners:
        dx = corner[0] - loc[0]
        dy = corner[1] - loc[1]
        dist = (dx ** 2 + dy ** 2) ** 0.5
        # If dx > 0, corner_x > loc_x, so the corner
        # is right of the agent.

        # If a corner is right and above or left and down
        if (dx > 0 and dy > 0) or (dx < 0 and dy < 0):
            cornertypes = (1, 2)
        else:
            cornertypes = (0, 3)
        if dist <= rng and corner in cornertypes:
            yield corner + (dist,)


# AUXILIARY
def get_rel_angle(a1, a2):
    """ Positive angle indicates a right turn. Relative call.
    """
    return angle_fix(math.atan2(a2[1]-a1[1], a2[0]-a1[0]) - a1[2])


def get_angle(a1, a2):
    """ Absolute call.
    """
    return math.atan2(a2[1]-a1[1], a2[0]-a1[0])


def angles_plus_dist(a1, a2, r, max_turn):
    """ Calculate angle relative to a1s orientation to the sides of
        a2, where a2 is a circle with radius r.
    """
    dist = point_dist(a1, a2)
    angle = get_rel_angle(a1, a2)
    angle_rel = math.asin(r / dist)
    left = max(angle - angle_rel, -max_turn)
    right = min(angle + angle_rel, max_turn)
    return (left, right, dist)


def collision(p1, p2, p3, p4, r=8):
    """Agent A goes from p1 to p2, agent B from p3 to p4.
    Returns True if paths collide.
    """

    # This may be redundant, but is possibly faster
    if p1 == p4 and p3 == p2:
        return True     # opposite directions
    # TODO: also check if they are really close

    # calculate intersection
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if d == 0:
        return False    # parallel

    a = (x1 * y2 - y1 * x2) * (x3 - x4)
    b = (x3 * y4 - y3 * x4)

    x = a - (x1 - x2) * b / d
    y = a - (y1 - y2) * b / d

    # Check intersection between path sections
    if between_on_line(p1, p2, (x, y)):
        da = point_dist(p1, (x, y))
        db = point_dist(p3, (x, y))
        diff = abs(da - db)
        # TODO:
        # Collision is dependent on how close da and db are (if they are the
        # same they happen at the same time), and the angle between the paths.
        # Calculate where distance between lines == radius*2, should be smaller
        # than diff for collision
        dist = r / math.sin(get_angle((p1, p2), (p3, p4)))
        if dist < diff and something:       # TODO check if not outside section
            return True
    return False


def between_on_line(a, b, c):
    """Return True if c between a and b. Assumes they are all on the same line
    """
    mn, mx = min_max(a[0], b[0])
    d = b[0] - mn
    if 0 > d > mx:
        return True
    return False


def min_max(a, b):
    if a < b:
        return a, b
    return b, a
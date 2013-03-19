

class Agent(object):

    NAME = "my_agent" # Replay filenames and console output will contain this name.

    def __init__(self, id, team, settings=None, field_rects=None, field_grid=None, nav_mesh=None,blob=None, **kwargs):
        
        self.blobpath = "agents/q/new2_"
        if os.path.isfile(self.blobpath):
            file = open(self.blobpath, "rb")
            self.QTable = pickle.load(file)
            file.close()
        else:
            self.QTable = [0] * 5000;

            for x in range(0,3479):
                self.QTable[x] =  [0.0015] * 646 * 2;


                

        self.Actions = [(0,0,False)] * 646;
        for a in range(-45,45,5):
            for s in range(-40,40,5):
                for c in range(0,1):
                    i  = a/5*16 + s/5*2 + c;
                    self.Actions[i] = (a,s,bool(c));

        self.last_observation = None;
        self.observation = None;
        self.old_action = (0,0,False);
        self.new_action = (0,0,False);
        self.old_index = 0;    
        self.new_index = 0;     

    def observe(self, observation):
        self.last_observation = self.observation;
        self.observation = observation;
               

    def action(self):
        
        """ This function is called every step and should
            return a tuple in the form: (turn, speed, shoot)
        """
        time_action = time.time()

        # Initialize shoot
        shoot = False

        # Drive to where the user clicked
        # Clicked is a list of tuples of (x, y, shift_down, is_selected)
        if self.observation.clicked:
            self.goal = self.observation.clicked[0][0:2]

        # Find the optimal path through the mesh
        if self.goal[:2] in self.paths:
            path, dist = self.paths[self.goal[:2]][:2]
        else:
            path, dist = self.find_optimal_path()[:2]

        # Convert path to useful movement info
        if path:
            node = path[0]
            dx = node[0] - self.loc[0]
            dy = node[1] - self.loc[1]

            if len(path) > 1 and abs(dx) < 1 and abs(dy) < 1:
                path.remove(node)
                node = path[0]
                dx = node[0] - self.loc[0]
                dy = node[1] - self.loc[1]

            angle = get_rel_angle(self.loc, node)

            if self.goal_reached():
                speed = 0
                turn = 0

                if len(self.goal) > 2:
                    turn = angle_fix(self.goal[2] - self.loc[2])

                elif self.ammo:
                    if self.foes:
                        closest_foe, dist = self.closest_foe()

                        if self.selected:
                            print closest_foe, dist
                        if dist / 40 < 5:
                            turn = get_rel_angle(self.loc, closest_foe)
                        else:
                            turn = angle_fix((self.team == TEAM_BLUE) * math.pi
                                    - self.loc[2])
                    else:
                        turn = angle_fix((self.team == TEAM_BLUE) * math.pi
                                - self.loc[2])

            elif abs(angle_fix(angle - math.pi)) < self.settings.max_turn:
                speed = -(dx**2 + dy**2)**0.5
                turn = angle_fix(angle - math.pi)
            else:
                speed = (dx**2 + dy**2)**0.5
                turn = angle_fix(angle)
        else:
            print 'ERROR: No path found to goal {0}'.format(self.goal)
            turn = 0
            speed = 0

        return (turn, speed, shoot)

    def choose_action(self):
        r = random.randint(0,1000)
        p = 0;
        act = random.randint(0,645);
        for x in range(646,2*646-1):
            p += self.QTable[self.new_index][x]*1000
            if(r<p): 
                act = x - 646
                break

        return self.Actions[act]


    def action_index(self,A):
        x = A[0] / 5;
        y = A[1] / 5;
        z = 0;
        if(A[2]):
            z = 1;

        i = x*2*17 + y*2 + z;
        if i > 646 : print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        return i;

    def index(self):
        x =  -1 + self.observation.loc[0]/16;
        y =  -1 + self.observation.loc[1]/16;
        angle = -1 + int(math.degrees(self.observation.angle)/12);
       
        i = x*15*8 + y*8 + angle;
        if i>3480 : print "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE"
        return i  

    def debug(self, surface):
        pass
      

    def PrintStuff(self):
        #print "Old State =: "
        print self.old_index;
        pass
        
    def Softmax(self):
        t = 3;
        sum = 0;
        for x in range(0,645):
            sum += math.pow(2.718,( self.QTable[self.old_index][x] / t ) );
        for y in range(646,2*646-1):
            self.QTable[self.old_index][y] = ( math.pow(2.718,( self.QTable[self.old_index][y-646] / t ) ) )  / sum ; 
 


        


    def UpdateQTable(self):

        self.QTable[self.old_index][self.action_index(self.old_action)] += 0.5 * (self.Reward + 0.7*self.QTable[self.new_index][self.action_index(self.new_action)] - self.QTable[self.old_index][self.action_index(self.old_action)] );

    def finalize(self, interrupted=False):
        """ This function is called after the game ends, 
            either due to time/score limits, or due to an
            interrupt (CTRL+C) by the user. Use it to
            store any learned variables and write logs/reports.
        """
        if self.blobpath is not None:
            try:
                print "writing the q table back..."
                file = open(self.blobpath, "wb")
                pickle.dump(self.QTable, file)
                file.close()
            except:
                # We can't write to the blob, this is normal on AppEngine since
                # we don't have filesystem access there.        
                print "Agent %s can't write blob."
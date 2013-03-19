class Agent(object):

    NAME = "my_agent" # Replay filenames and console output will contain this name.

    def __init__(self, id, team, settings=None, field_rects=None, field_grid=None, nav_mesh=None, **kwargs):
        
        #Load or Create Q Table
        self.blobpath = "agents/q/new2"
        if os.path.isfile(self.blobpath):
            file = open(self.blobpath, "rb")
            self.QTable = pickle.load(file)
            file.close()
        else:
            self.QTable = [0] * 3480;
            for x in range(0,3480):
                self.QTable[x] =  [10] * 42;


        #Create Policy Table
        self.PTable = [0] * 3480;
        for x in range(0,3480):
                self.PTable[x] =  [0.0238095238] * 42;

        #Create Actions Reference Table
        self.Actions = [(0,0,False)] * 42;
        a_i = 0
        s_i = 0
        for a in range(-45,45,45):
            for s in range(-48,48,16):
                for c in range(0,1):
                    i  = (a_i)*7 + (s_i)*2 + c;
                    self.Actions[i] = (a,s,bool(c));
                s_i = s_i + 1
            a_i = a_i + 1
                    

        #Sarsa Components
        self.Reward = 0;
        self.old_action_index = 0;
        self.new_action_index = 0;
        self.old_state_index = 0;    
        self.new_state_index = 0; 
        self.last_observation = None;
        self.observation = None; 

        pass

    def observe(self, observation):
        self.last_observation = self.observation;
        self.observation = observation;
        pass

    def action(self):
        self.old_action_index = self.new_action_index;
        self.old_state_index = self.new_state_index;
        self.new_state_index = self.index(self.observation);
        self.new_action_index = self.choose_action();
        self.Reward = 0;
        if self.new_state_index == 1584 :
            self.Reward = 10;
        
        self.UpdateQTable();
        self.Softmax();

        self.PrintStuff();
        return self.Actions[self.new_action_index]

    def index(self,observation):
        x =  -1 + observation.loc[0]/16;
        y =  -1 + observation.loc[1]/16;
        angle = -1 + int(math.degrees(observation.angle)/12);
       
        i = x*15*8 + y*8 + angle;
        return i  


    def choose_action(self):
        r = random.randint(0,1000)
        p = 0;
        for x in range(42):
            p += self.PTable[self.new_state_index][x]*1000
            if(r<p): 
                act = x 
                break

        return act

    def Softmax(self):
        t = 3;
        sum = 0;
        for x in range(0,41):
            sum += math.pow(2.718,( self.QTable[self.old_state_index][x] / t ) );
        for y in range(0,41):
            self.PTable[self.old_state_index][y] = ( math.pow(2.718,( self.QTable[self.old_state_index][y] / t ) ) )  / sum ; 

    def UpdateQTable(self):
        self.QTable[self.old_state_index][self.old_action_index] += 0.5 * (self.Reward + 0.7*self.QTable[self.new_state_index][self.new_action_index] - self.QTable[self.old_state_index][self.old_action_index] )
        pass

    def PrintStuff(self):
        print self.old_state_index;
        pass

    def debug(self, surface):
        self.PrintStuff();
        pass

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
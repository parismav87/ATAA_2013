

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
        pass

    def action(self):
        self.Reward = 0;
        if self.last_observation is not None:
            if self.last_observation.loc[0] == self.last_observation.cps[0][0] and self.last_observation.loc[1] == self.last_observation.cps[0][1] :
                print "hereeeeeeeeeeeeeeeeeeeeee"
                self.Reward =  50;

        self.UpdateQTable();
        self.Softmax();
        self.old_action = self.new_action;
        self.old_index = self.new_index;
        self.new_index = self.index();
        self.new_action =  self.choose_action();

        self.PrintStuff();
        return self.new_action

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
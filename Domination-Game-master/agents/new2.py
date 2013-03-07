

class Agent(object):

    NAME = "my_agent" # Replay filenames and console output will contain this name.

    def __init__(self, id, team, settings=None, field_rects=None, field_grid=None, nav_mesh=None, **kwargs):
        self.QTable = [0] * 5000;

        for x in range(0,5000):
            self.QTable[x] =  [0] * 1000;

        self.observation = 0;
        self.old_action = (0,0,False);
        self.new_action = (0,0,False);
        self.old_index = 0;    
        self.new_index = 0;     

    def observe(self, observation):
        #self.old_observation = self.observation;
        self.observation = observation;
        pass

    def action(self):

        self.UpdateQTable();
        self.old_action = self.new_action;
        self.old_index = self.new_index;
        self.new_index = self.index();
        
        self.Reward = 0;
        if(self.observation.loc[0] == 10 and self.observation.loc[1] == 10 )
            self.Reward =  10;

        self.new_action = self.choose_action();

        self.PrintStuff();
        return self.new_action

    def choose_action(self):

        a = random.randint(0,49);
        a = a - a%5;
        b = random.randint(0,44);
        b = b - b%5;
        c = bool(random.randint(0,1));
        return (a,b,c)

    def action_index(self,A):
        x = A[0] / 5;
        y = A[1] / 5;
        z = 0;
        if(A[2]):
            z = 1;

        i = x*18 + y*2 + z;

        return i;

    def index(self):
        x = self.observation.loc[0]/16;
        y = self.observation.loc[1]/16;
        angle = int(math.degrees(self.observation.angle)/12);
        i = x*15*8 + y*8 + angle;
        return i  

    def debug(self, surface):
        pass
      

    def PrintStuff(self):
        print "Old State =: "
        print self.old_index;
        print "Old Action =: "
        print self.old_action;
        print "New State =: "
        print self.new_index;
        print "New Action =: "
        print self.new_action;
        


    def UpdateQTable(self):

        self.QTable[self.old_index][self.action_index(self.old_action)] = 10;

    def finalize(self, interrupted=False):
        pass
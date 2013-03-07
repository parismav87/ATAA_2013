class Agent(object):

    NAME = "my_agent" # Replay filenames and console output will contain this name.

    def __init__(self, id, team, settings=None, field_rects=None, field_grid=None, nav_mesh=None, **kwargs):
        QTable = list();
        #self.observation = 0;
        #self.action = 0;
        pass

    def observe(self, observation):
        #self.old_observation = self.observation;
        self.observation = observation;
        pass

    def action(self):

        #self.old_action = self.action;

        a = random.randint(0,45);
        b = random.randint(0,40);
        c = random.randint(0,1);

        #self.action = (a,b,c)

        print self.index()
        return (a,b,True) #self.action

    def index(self):
        x = self.observation.loc[0]/16;
        y = self.observation.loc[1]/16;
        angle = int(math.degrees(self.observation.angle)/12);
        i = x*15*8 + y*8 + angle;
        return i  

    def debug(self, surface):
        pass
      

    def UpdateQTable(self):
        QTable[index()] = 10;

    def finalize(self, interrupted=False):
        pass
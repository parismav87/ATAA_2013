class Agent(object):

    NAME = "my_agent" # Replay filenames and console output will contain this name.

    def __init__(self, id, team, settings=None, field_rects=None, field_grid=None, nav_mesh=None, **kwargs):
        pass

    def observe(self, observation):
		self.observation = observation
        

    def action(self):
		a = random.randint(0,45);
		b = random.randint(0,40);
		c = random.randint(0,1);
        return (a,b,c);

	def createQTable(self):
        Qtable = dict();

	def index(self)
		x = self.observation.loc[0];
		y = self.observation.loc[1];
		angle = self.observation.angle;
		i = x*15*8 + y*8 + angle;
		return i;
		
    def debug(self, surface):
		print self.index()
        
	
    def finalize(self, interrupted=False):
        pass
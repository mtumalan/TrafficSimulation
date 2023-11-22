from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import *
import json
import os

class CityModel(Model):
    """ 
        Creates a model based on a city map.

        Args:
            N: Number of agents in the simulation
    """
    def __init__(self, N):

        # Load the map dictionary. The dictionary maps the characters in the map file to the corresponding agent.
        mapAbsPath = os.path.abspath("./city_files/mapDictionary.json")
        dataDictionary = json.load(open(mapAbsPath))

        self.traffic_lights = []

        # Load the map file. The map file is a text file where each character represents an agent.
        with open('city_files/2022_base.txt') as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0])-1
            self.height = len(lines)

            self.grid = MultiGrid(self.width, self.height, torus = False) 
            self.schedule = RandomActivation(self)

            # Goes through each character in the map file and creates the corresponding agent.
            for r, row in enumerate(lines):
                for c, col in enumerate(row):
                    if col in ["v", "^", ">", "<"]:
                        agent = Road(f"r_{r*self.width+c}", self, dataDictionary[col])
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col in ["S", "s"]:
                        agent = Traffic_Light(f"tl_{r*self.width+c}", self, False if col == "S" else True, int(dataDictionary[col]))
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)
                        self.traffic_lights.append(agent)

                    elif col == "#":
                        agent = Obstacle(f"ob_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col == "D":
                        agent = Destination(f"d_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)

        self.num_agents = N
        self.running = True
        self.step_count = 0
        
    def set_destination(self):
        """
        Set the destination of the car.
        """
        destinations = [] # List of all the destinations
        for agent in self.schedule.agents: # Iterate through all the agents
            if isinstance(agent, Destination): # If the agent is a destination,
                destinations.append(agent.pos) # Add the position of the destination to the list of destinations
        #print(f"Number of destinations: {len(destinations)}")
        return self.random.choice(destinations) if destinations else None # Return a random destination if there are any destinations, otherwise return None

    def create_car(self):
        """
        Create cars agent and add them to the model.
        """
        corners = [(0, 0), (self.width-1, 0), (0, self.height-2), (self.width-1, self.height-2)] # List of all the corners of the grid
        for corner in corners: # Iterate through all the corners
            print(f"Placing car at: {corner}")
            if 0 <= corner[0] < self.height and 0 <= corner[1] < self.width: # If the corner is valid,
                destination = self.set_destination()  # Set the destination of the car
                #print(f"Destination: {destination}")
                agent = Car(f"Car_{self.num_agents + 1}", self, corner, destination)  # Create a unique ID for the car, and pass the model and the destination
                self.grid.place_agent(agent, corner)  # Place the car on the grid
                agent.initialize_path()  # Initialize the path after placing the car
                self.schedule.add(agent)  # Add the car to the scheduler
                self.num_agents += 1  # Increment the number of agents
            else: # If the corner is invalid,
                print(f"Invalid corner: {corner}")
    
    def remove_car(self, agent):
        """
        Remove a car from the model.
        """
        self.schedule.remove(agent) # Remove the agent from the scheduler
        self.grid.remove_agent(agent) # Remove the agent from the grid


    def step(self):
        '''Advance the model by one step.'''
        self.step_count += 1 # Increment the step count
        if self.step_count == 1:
            self.create_car() # Create cars at the beginning of the simulation
        if self.step_count % 10 == 0:
            self.create_car()  # Create new cars every 10 steps
        self.schedule.step()
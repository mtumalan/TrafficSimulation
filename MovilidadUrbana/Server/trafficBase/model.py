from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import *
import json
import os
import requests

class CityModel(Model):
    """ 
        Creates a model based on a city map.

        Args:
            N: Number of agents in the simulation
    """
    def __init__(self, N):
#C:\Users\carlo\OneDrive\Escritorio\2023\ITESM\MULTIAGENTES\PROYECTOR\activities_TC2008B\MovilidadUrbana\Server\trafficBase\city_files
        # Load the map dictionary. The dictionary maps the characters in the map file to the corresponding agent.
        mapAbsPath = os.path.abspath("city_files/mapDictionary.json")#("MovilidadUrbana/Server/trafficBase/city_files/mapDictionary.json")
        dataDictionary = json.load(open(mapAbsPath)) # Load the map dictionary. The dictionary maps the characters in the map file to the corresponding agent.

        self.traffic_lights = [] # List of all the traffic lights
        self.car_removed = 0 # Number of cars that have reached their destination

        # Load the map file. The map file is a text file where each character represents an agent.
        with open("city_files/2023_base.txt") as baseFile:#('MovilidadUrbana/Server/trafficBase/city_files/2022_base.txt') as baseFile:
            lines = baseFile.readlines() # Read the lines of the map file
            self.width = len(lines[0])-1 # Width of the map
            self.height = len(lines) # Height of the map

            self.grid = MultiGrid(self.width, self.height, torus = False) # Create a grid with the width and height of the map
            self.schedule = RandomActivation(self) # Create a random activation scheduler

            # Goes through each character in the map file and creates the corresponding agent.
            for r, row in enumerate(lines): # Iterate through the lines of the map file
                for c, col in enumerate(row): # Iterate through the characters of the line
                    if col in ["v", "^", ">", "<"]: # If the character is a road,
                        agent = Road(f"r_{r*self.width+c}", self, dataDictionary[col]) # Create a road agent
                        self.grid.place_agent(agent, (c, self.height - r - 1)) # Place the agent on the grid

                    elif col in ["S", "s"]: # If the character is a traffic light,
                        agent = Traffic_Light(f"tl_{r*self.width+c}", self, False if col == "S" else True, int(dataDictionary[col])) # Create a traffic light agent
                        self.grid.place_agent(agent, (c, self.height - r - 1)) # Place the agent on the grid
                        self.schedule.add(agent) # Add the agent to the scheduler
                        self.traffic_lights.append(agent) # Add the agent to the list of traffic lights

                    elif col == "#": # If the character is an obstacle,
                        agent = Obstacle(f"ob_{r*self.width+c}", self) # Create an obstacle agent
                        self.grid.place_agent(agent, (c, self.height - r - 1)) # Place the agent on the grid

                    elif col == "D": # If the character is a destination,
                        agent = Destination(f"d_{r*self.width+c}", self) # Create a destination agent
                        self.grid.place_agent(agent, (c, self.height - r - 1)) # Place the agent on the grid
                        self.schedule.add(agent) # Add the agent to the scheduler

        self.num_agents = N # Number of agents in the simulation
        self.running = True # Whether the simulation is running or not
        self.step_count = 0 # Number of steps in the simulation
        
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
            #print(f"Placing car at: {corner}")
            if 0 <= corner[0] < self.height and 0 <= corner[1] < self.width: # If the corner is valid,
                cell_contents = self.grid.get_cell_list_contents([corner]) # Get the contents of the cell
                if not any(isinstance(agent, Car) for agent in cell_contents):
                    destination = self.set_destination()  # Set the destination of the car
                    agent = Car(f"Car_{self.num_agents + 1}", self, corner, destination)  # Create a unique ID for the car, and pass the model and the destination
                    self.grid.place_agent(agent, corner)  # Place the car on the grid
                    agent.initialize_path(0)  # Initialize the path after placing the car
                    self.schedule.add(agent)  # Add the car to the scheduler
                    self.num_agents += 1  # Increment the number of agents
                else:
                    print(f"There is already a car in corner: {corner}")
            else: # If the corner is invalid,
                print(f"Invalid corner: {corner}") # Print the invalid corner
    
    def remove_car(self, agent):
        """
        Remove a car from the model.
        """
        self.schedule.remove(agent) # Remove the agent from the scheduler
        self.grid.remove_agent(agent) # Remove the agent from the grid
    def postCar(self):
        url = "http://52.1.3.19:8585/api/attempts" #http://52.1.3.19:8585/api/validate_attempt

        data = {
            "year" : 2023,
            "classroom" : 301,
            "name" : "Equipo 11: carlos y mau mesa",
            "num_cars": self.car_removed
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, data=json.dumps(data), headers=headers)
        print(data)
        print("Request " + "successful" if response.status_code == 200 else "failed", "Status code:", response.status_code)
        print("Response:", response.json())

    def step(self):
        '''Advance the model by one step.'''
        self.step_count += 1 # Increment the step count
        #print("step: ", self.step_count)
        if self.step_count == 1:
            self.create_car() # Create cars at the beginning of the simulation
        if self.step_count % 3 == 0:
            self.create_car()  # Create new cars every 10 steps
        if self.step_count % 100 == 0:
            print("CAR REMOVED", self.car_removed)
            #self.postCar() #Postea los carros que llegaron a su destino
        self.schedule.step()
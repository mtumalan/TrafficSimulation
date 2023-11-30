from mesa import Agent
import heapq
import random

def heuristic(a, b):
    """
    Returns the Manhattan distance between two cells.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(graph, start, goal, pathclear):
    """
    Finds the shortest path between two cells using A*.
    """
    print(f"Starting A* search from {start} to {goal}")
    obstacles = [] # Priority queue
    heapq.heappush(obstacles, (0, start)) # Add start cell to queue
    wherefrom = {start: None} # Dictionary to keep track of where the path came from
    sofar = {start: 0} # Dictionary to keep track of the cost so far
    
    while not len(obstacles) == 0:
        current = heapq.heappop(obstacles)[1] # Get the cell with the lowest cost
        #print(f"Checking cell: {current}")
        if current == goal: # If the goal is reached, stop
            #print("Goal reached in A* search")
            break
        for next in graph.get_neighborhood(current, moore=False, include_center=False): # Get the neighbors of the current cell
            if not pathclear(current, next): # If the path is not clear,
                continue # Skip this neighbor
            new_cost = sofar[current] + 1 # Calculate the cost to get to the neighbor
            if next not in sofar or new_cost < sofar[next]: # If the neighbor has not been visited or the cost is lower than the previous cost,
                sofar[next] = new_cost # Update the cost
                priority = new_cost + heuristic(goal, next) # Calculate the priority
                heapq.heappush(obstacles, (priority, next)) # Add the neighbor to the queue
                wherefrom[next] = current # Update the path
    path = {} # Dictionary to keep track of the path
    current = goal # Start at the goal
    while current != start: # While the start is not reached,
        if current in wherefrom: # If the current cell is in the path,
            prev = wherefrom[current] # Get the previous cell
            path[prev] = current  # Map predecessor to current position
            current = prev # Update the current cell
        else: # If the current cell is not in the path,
            print("No path found in A* search")
            return {}  # Return empty path if no path is found

    print(f"Path found: {path}")
    return path # Return the path

class Car(Agent):
    """
    Agent that moves towards a destination using A*.
    """
    def __init__(self, unique_id, model, spawn, destination = None):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            spawn: Where the agent is spawned
            destination: Where the agent is going
        """
        super().__init__(unique_id, model)
        self.destination = destination
        self.spawn = spawn
        self.path = None
        self.greediness = random.randint(0, 100)
        #self.status = False
        #self.stepsCrash = 0
    
    def initialize_path(self):
        """
        Initializes the path for the agent.
        """
        self.path = self.find_path()

    def is_direction_valid(self, current_pos, next_pos, road_direction):
        """
        Checks if moving from current_pos to next_pos is valid based on the road_direction.
        Allow diagonal movement only if there is movement in the allowed direction.
        """
        dx = next_pos[0] - current_pos[0]  # Change in x
        dy = next_pos[1] - current_pos[1]  # Change in y

        if road_direction == "Right":  # If the road is going right,
            return dx != -1   # Moving left is not allowed, only horizontal movement
        elif road_direction == "Left":  # If the road is going left,
            return dx != 1   # Moving right is not allowed, only horizontal movement
        elif road_direction == "Up":  # If the road is going up,
            return dy != -1  # Moving down is not allowed, only vertical movement
        elif road_direction == "Down":  # If the road is going down,
            return dy != 1   # Moving up is not allowed, only vertical movement

        return False  # If the road direction is invalid, return False

    def find_path(self):
        """
        Finds the path from spawn to destination.
        """
        if self.destination: # If the destination is set,
            #print(f"Finding path for Car {self.unique_id} from {self.spawn} to {self.destination}")
            def pathclear(current, next): # Function to check if the path is clear
                cell_contents = self.model.grid.get_cell_list_contents([next]) # Get the contents of the next cell

                # Check if the next cell contains an obstacle
                if any(isinstance(agent, Obstacle) for agent in cell_contents):
                    #print(f"Obstacle found at {next}")  # Debug
                    return False

                # Check if the next cell is a road, traffic light, or destination
                if any(isinstance(agent, (Road, Traffic_Light, Destination)) for agent in cell_contents):
                    # If it's a road, check the direction
                    roads = [agent for agent in cell_contents if isinstance(agent, Road)]
                    if roads: # If there is a road in the cell
                        road = roads[0]  # Get the first road
                        return self.is_direction_valid(current, next, road.direction) # Check if the direction is valid
                    return True  # If it's a traffic light or destination, movement is allowed
                return False  # Cell without road, traffic light, or destination is not valid
            return a_star_search(self.model.grid, self.spawn, self.destination, pathclear) # Find the path
        print("No destination set for Car, no path to find")  # in case the destination is not reachable or not able to be set
        return None # If the destination is not set, return None


    def move(self):
        """ 
        Determines if the agent can move in the direction that was chosen
        """        
        descuido = random.randint(0, 200) < self.greediness
        if self.path and self.pos in self.path: # If the path is set and the current position is in the path,
            if isinstance(self.model.grid[self.path.get(self.pos)[0]][self.path.get(self.pos)[1]], list):
                # Itera sobre los agentes en la lista
                for agent_in_cell in self.model.grid[self.path.get(self.pos)[0]][self.path.get(self.pos)[1]]:
                    if type(agent_in_cell) == Car: #and (random.randint(0, 500) < self.greediness) == False: #descuido choque
                        next_pos = self.pos
                    elif type(agent_in_cell) == Traffic_Light and descuido == False:
                        if agent_in_cell.state == False:
                            next_pos = self.pos
                        else:
                            next_pos = self.path.get(self.pos) # Get the next position
                    else:
                        next_pos = self.path.get(self.pos) # Get the next position
            next_next_pos = self.path.get(next_pos)
            if next_next_pos is not None and descuido == False:
                road_direction_at_pos = "beg"
                road_direction_at_next_next_pos = "beg"
                if isinstance(self.model.grid[self.pos[0]][self.pos[1]], list):
                    # Itera sobre los agentes en la lista
                    for agent_in_cell in self.model.grid[self.pos[0]][self.pos[1]]:
                        if type(agent_in_cell) == Road:
                            road_direction_at_pos = agent_in_cell.direction
                if isinstance(self.model.grid[next_next_pos[0]][next_next_pos[1]], list):
                    # Itera sobre los agentes en la lista
                    for agent_in_cell in self.model.grid[next_next_pos[0]][next_next_pos[1]]:
                        if type(agent_in_cell) == Road:
                            road_direction_at_next_next_pos = agent_in_cell.direction
                        if type(agent_in_cell) == Car:
                            road_direction_at_pos = "no"
                
                if self.needs_lane_change(self.pos, next_next_pos, road_direction_at_pos, road_direction_at_next_next_pos):
                    print(f"Car {self.unique_id} is changing lanes from {self.pos} to {next_next_pos}")
                    next_pos = next_next_pos
            """
            if isinstance(self.model.grid[self.path.get(self.pos)[0]][self.path.get(self.pos)[1]], list):
                # Itera sobre los agentes en la lista
                for agent_in_cell in self.model.grid[self.path.get(self.pos)[0]][self.path.get(self.pos)[1]]:
                    if type(agent_in_cell) == Car and agent_in_cell.status:
                        next_pos = self.avoid_collision(agent_in_cell) #-AQUI- se consigue la coordenada que se quiere
                        self.path[next_pos] = self.path.pop(self.pos)
                        print(self.pos)
                        print(next_pos)
            """

            if next_pos is not None: # If the next position is not None,
                self.model.grid.move_agent(self, next_pos) # Move the agent to the next position
                self.direction = self.get_direction(self.pos, next_pos) # Get the direction the agent should face
                if next_pos == self.destination: # If the destination is reached,
                    print(f"Car {self.unique_id} reached destination {self.destination}") 
                    self.model.remove_car(self) # Remove the car from the model
                    self.model.car_removed = self.model.car_removed + 1
            else: # If the next position is None,
                print("No valid next position found.") 
    def avoid_collision(self,nextCar):
        road_direction_at_next_pos = "beg"
        if isinstance(self.model.grid[nextCar.pos[0]][nextCar.pos[1]], list):
            # Itera sobre los agentes en la lista
            for agent_in_cell in self.model.grid[nextCar.pos[0]][nextCar.pos[1]]:
                if type(agent_in_cell) == Road:
                    road_direction_at_next_pos = agent_in_cell.direction
        print(road_direction_at_next_pos)
        if ( road_direction_at_next_pos == "Up" or road_direction_at_next_pos == "Down" ):
            if isinstance(self.model.grid[nextCar.pos[0]-1][nextCar.pos[1]], list):
                # Itera sobre los agentes en la lista
                for agent_in_cell in self.model.grid[nextCar.pos[0]-1][nextCar.pos[1]]:
                    if type(agent_in_cell) == Road and agent_in_cell.direction == road_direction_at_next_pos:
                        return (nextCar.pos[0]- 1,nextCar.pos[1])
            if isinstance(self.model.grid[nextCar.pos[0]+1][nextCar.pos[1]], list):
                # Itera sobre los agentes en la lista
                for agent_in_cell in self.model.grid[nextCar.pos[0]+1][nextCar.pos[1]]:
                    if type(agent_in_cell) == Road and agent_in_cell.direction == road_direction_at_next_pos:
                        return (nextCar.pos[0]+1,nextCar.pos[1])
        if ( road_direction_at_next_pos == "Left" or road_direction_at_next_pos == "Right" ):
            if isinstance(self.model.grid[nextCar.pos[0]][nextCar.pos[1]-1], list):
                # Itera sobre los agentes en la lista
                for agent_in_cell in self.model.grid[nextCar.pos[0]][nextCar.pos[1]-1]:
                    if type(agent_in_cell) == Road and agent_in_cell.direction == road_direction_at_next_pos:
                        return (nextCar.pos[0],nextCar.pos[1]-1)
            if isinstance(self.model.grid[nextCar.pos[0]][nextCar.pos[1]+1], list):
                # Itera sobre los agentes en la lista
                for agent_in_cell in self.model.grid[nextCar.pos[0]][nextCar.pos[1]+1]:
                    if type(agent_in_cell) == Road and agent_in_cell.direction == road_direction_at_next_pos:
                        return (nextCar.pos[0],nextCar.pos[1]+1)
        

    def needs_lane_change(self,current_pos, next_next_pos, road_direction_at_pos, road_direction_at_next_next_pos):
        """
        Verifies if a lane change is necessary based on the road directions at the current and next_next positions.
        """
        if road_direction_at_pos == road_direction_at_next_next_pos or road_direction_at_pos == "beg":
            if ( road_direction_at_next_next_pos == "Up" or road_direction_at_next_next_pos == "Down" ) and (next_next_pos[0] - current_pos[0]) != 0:
                return True
            if ( road_direction_at_next_next_pos == "Left" or road_direction_at_next_next_pos == "Right" ) and (next_next_pos[1] - current_pos[1]) != 0:
                return True

        # If neither x nor y changed, no lane change is needed
        return False

    def is_front_valid(self, next):
        neighbor_info = []
        cell_content = self.model.grid[next[0]][next[1]]
        # Verifica si la celda contiene una lista
        if isinstance(cell_content, list):
            # Itera sobre los agentes en la lista
            for agent_in_cell in cell_content:

                # Agrega una tupla a la lista con la posición y el tipo de agente
                neighbor_info.append(((next[0], next[1]), type(agent_in_cell)))
        return 1
        
    def get_direction(self, current_pos, next_pos):
        """
        Determines the direction the agent should face after moving.
        """
        dx = next_pos[0] - current_pos[0] # Change in x
        dy = next_pos[1] - current_pos[1] # Change in y
        if dx == 1: # If the agent moved right,
            return "Right"
        elif dx == -1: # If the agent moved left,
            return "Left"
        elif dy == -1: # If the agent moved up,
            return "Up"
        elif dy == 1: # If the agent moved down,
            return "Down"
        else: # If the agent didn't move,
            return None

    def step(self): 
        """ 
        Determines the new direction it will take, and then moves
        if isinstance(self.model.grid[self.pos[0]][self.pos[1]], list):
            for agent_in_cell in self.model.grid[self.pos[0]][self.pos[1]]:
                if type(agent_in_cell) == Car and agent_in_cell.unique_id != self.unique_id:
                    self.status = True #chocado
        if self.status == False:
            self.move()
        elif self.status == True:
            self.stepsCrash = self.stepsCrash + 1
            if self.stepsCrash > 10:
                self.model.remove_car(self)
        """
        self.move()

class Traffic_Light(Agent):
    """
    Traffic light. Where the traffic lights are in the grid.
    """
    def __init__(self, unique_id, model, state = False, timeToChange = 10):
        super().__init__(unique_id, model)
        """
        Creates a new Traffic light.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            state: Whether the traffic light is green or red
            timeToChange: After how many step should the traffic light change color 
        """
        self.state = state
        self.timeToChange = timeToChange

    def step(self):
        """ 
        To change the state (green or red) of the traffic light in case you consider the time to change of each traffic light.
        """
        if self.model.schedule.steps % self.timeToChange == 0:
            self.state = not self.state

class Destination(Agent):
    """
    Destination agent. Where each car should go.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Obstacle(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Road(Agent):
    """
    Road agent. Determines where the cars can move, and in which direction.
    """
    def __init__(self, unique_id, model, direction= "Left"):
        """
        Creates a new road.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            direction: Direction where the cars can move
        """
        super().__init__(unique_id, model)
        self.direction = direction

    def step(self):
        pass
from flask import Flask, request, jsonify
from model import CityModel
from agent import Car, Obstacle, Traffic_Light, Destination, Road

# Size of the board:
number_agents = 5
cityModel = None
currentStep = 0
    
app = Flask("Traffic example")

@app.route('/init', methods=['POST'])
def initModel():
    global currentStep, cityModel, number_agents
    cityModel = CityModel(number_agents)
    return jsonify({"message":"Parameters recieved, model initiated."})

@app.route('/getAgents', methods=['GET'])
def getAgents():
    global cityModel

    if request.method == 'GET':
        carPositions = [{"id": str(car.unique_id), "x": x, "y": 0, "z": z}
                for x in range(cityModel.grid.width)
                for z in range(cityModel.grid.height)
                for car in cityModel.grid.get_cell_list_contents((x, z))
                if isinstance(car, Car)]

        return jsonify({'positions':carPositions})
    
@app.route('/getObstacles', methods=['GET'])
def getObstacles():
    global cityModel

    if request.method == 'GET':
        obstaclePositions = [{"id": str(obstacle.unique_id), "x": x, "y": 0, "z": z}
                for x in range(cityModel.grid.width)
                for z in range(cityModel.grid.height)
                for obstacle in cityModel.grid.get_cell_list_contents((x, z))
                if isinstance(obstacle, Obstacle)]


        return jsonify({'positions':obstaclePositions})
    
@app.route('/getTrafficLights', methods=['GET'])
def getTrafficLights():
    global cityModel

    if request.method == 'GET':
        trafficLightPositions = [{"id": str(trafficLight.unique_id), "x": x, "y":0, "z":z, "state":trafficLight.state}
                                 for x in range(cityModel.grid.width)
                                 for z in range(cityModel.grid.height)
                                 for trafficLight in cityModel.grid.get_cell_list_contents((x, z))
                                 if isinstance(trafficLight, Traffic_Light)]
        
        return jsonify({'positions':trafficLightPositions})

@app.route('/getDestinations', methods=['GET'])
def getDestinations():
    global cityModel

    if request.method == 'GET':
        destinationPositions = [{"id": str(destination.unique_id), "x": x, "y":0, "z":z}
                                for x in range(cityModel.grid.width)
                                for z in range(cityModel.grid.height)
                                for destination in cityModel.grid.get_cell_list_contents((x, z))
                                if isinstance(destination, Destination)]

        return jsonify({'positions':destinationPositions})
    
@app.route('/getRoads', methods=['GET'])
def getRoads():
    global cityModel

    if request.method == 'GET':
        roadPositions = [{"id": str(road.unique_id), "x": x, "y":0, "z":z}
                         for x in range(cityModel.grid.width)
                         for z in range(cityModel.grid.height)
                         for road in cityModel.grid.get_cell_list_contents((x, z))
                         if isinstance(road, Road)]

        return jsonify({'positions':roadPositions})
    
@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, cityModel
    if request.method == 'GET':
        if cityModel is None:
            return jsonify({'error': 'Model not initialized, call /init.'}), 400
        cityModel.step()
        currentStep += 1
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})


if __name__=='__main__':
    app.run(host='localhost', port=8585, debug=True)
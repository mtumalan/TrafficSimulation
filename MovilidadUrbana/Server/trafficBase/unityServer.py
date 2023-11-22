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

    if request.method == 'POST':
        number_agents = int(request.form.get('NAgents'))
        width = int(request.form.get('width'))
        height = int(request.form.get('height'))
        currentStep = 0

        print(request.form)
        print(number_agents, width, height)
        cityModel = CityModel(number_agents)

        return jsonify({"message":"Parameters recieved, model initiated."})

@app.route('/getAgents', methods=['GET'])
def getAgents():
    global cityModel

    if request.method == 'GET':
        agentPositions = [{"id": str(a.unique_id), "x": x, "y":1, "z":z} for a, (x, z) in cityModel.grid.coord_iter() if isinstance(a, Car)]

        return jsonify({'positions':agentPositions})
    
@app.route('/getObstacles', methods=['GET'])
def getObstacles():
    global cityModel

    if request.method == 'GET':
        carPositions = [{"id": str(a.unique_id), "x": x, "y":1, "z":z} for a, (x, z) in cityModel.grid.coord_iter() if isinstance(a, Obstacle)]

        return jsonify({'positions':carPositions})
    
@app.route('/getTrafficLights', methods=['GET'])
def getTrafficLights():
    global cityModel

    if request.method == 'GET':
        trafficLightPositions = [{"id": str(a.unique_id), "x": x, "y":1, "z":z} for a, (x, z) in cityModel.grid.coord_iter() if isinstance(a, Traffic_Light)]

        return jsonify({'positions':trafficLightPositions})

@app.route('/getDestinations', methods=['GET'])
def getDestinations():
    global cityModel

    if request.method == 'GET':
        destinationPositions = [{"id": str(a.unique_id), "x": x, "y":1, "z":z} for a, (x, z) in cityModel.grid.coord_iter() if isinstance(a, Destination)]

        return jsonify({'positions':destinationPositions})
    
@app.route('/getRoads', methods=['GET'])
def getRoads():
    global cityModel

    if request.method == 'GET':
        roadPositions = [{"id": str(a.unique_id), "x": x, "y":1, "z":z} for a, (x, z) in cityModel.grid.coord_iter() if isinstance(a, Road)]

        return jsonify({'positions':roadPositions})
    
@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, cityModel
    if request.method == 'GET':
        cityModel.step()
        currentStep += 1
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})

if __name__=='__main__':
    app.run(host='localhost', port=8585, debug=True)
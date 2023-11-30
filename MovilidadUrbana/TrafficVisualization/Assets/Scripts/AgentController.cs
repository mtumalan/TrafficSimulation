// TC2008B. Sistemas Multiagentes y Gráficas Computacionales
// C# client to interact with Python. Based on the code provided by Octavio Navarro.
// Mau Tumalán, November 2023

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

[Serializable]
public class AgentData
{
    /*
    The AgentData class is used to store the data of each agent.
    
    Attributes:
        id (string): The id of the agent.
        x (float): The x coordinate of the agent.
        y (float): The y coordinate of the agent.
        z (float): The z coordinate of the agent.
    */
    public string id;
    public float x, y, z;

    public AgentData(string id, float x, float y, float z)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
    }
}

[Serializable]
public class StreetLightData : AgentData
{
    public bool state;

    public StreetLightData(string id, float x, float y, float z, bool state) : base(id, x, y, z)
    {
        this.state = state;
    }
}

[Serializable]

public class AgentsData
{
    /*
    The AgentsData class is used to store the data of all the agents.

    Attributes:
        positions (list): A list of AgentData objects.
    */
    public List<AgentData> positions;

    public AgentsData() => this.positions = new List<AgentData>();
}

[Serializable]
public class StreetLightsData
{
    public List<StreetLightData> positions;

    public StreetLightsData() => this.positions = new List<StreetLightData>();

}

public class AgentController : MonoBehaviour
{
    string serverUrl = "http://localhost:8585";
    string getAgentsEndpoint = "/getAgents";
    string getObstaclesEndpoint = "/getObstacles";
    string getTrafficLightsEndpoint = "/getTrafficLights";
    string getRoadsEndpoint = "/getRoads";
    string getDestinationsEndpoint = "/getDestinations";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";
    public AgentsData agentsData;
    public AgentsData obstacleData;
    public AgentsData roadData; 
    public AgentsData destinationData;
    public StreetLightsData streetLightData;
    Dictionary<string, GameObject> agents;
    Dictionary<string, GameObject> streetLights;
    Dictionary<string, Vector3> prevPositions, currPositions;

    bool updated = false, started = false;

    public GameObject agentPrefab, obstaclePrefab, trafficlightPrefab, roadPrefab, destinationPrefab;
    public int NAgents, width, height;
    public float timeToUpdate = 5.0f;
    private float timer, dt;

    void Start()
    {
        agentsData = new AgentsData();
        obstacleData = new AgentsData();
        streetLightData = new StreetLightsData();
        roadData = new AgentsData();
        destinationData = new AgentsData();

        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();

        agents = new Dictionary<string, GameObject>();
        streetLights = new Dictionary<string, GameObject>();
        
        timer = timeToUpdate;

        // Launches a couroutine to send the configuration to the server.
        StartCoroutine(SendConfiguration());
    }

    private void Update() 
    {
        if(timer < 0)
        {
            timer = timeToUpdate;
            updated = false;
            StartCoroutine(UpdateSimulation());
        }
        else{
            timer -= Time.deltaTime;
        }

        if (updated)
        {
            dt = 1.0f - (timer / timeToUpdate);

            foreach(var agent in currPositions)
            {
                Vector3 currentPosition = agent.Value;
                Vector3 previousPosition = prevPositions[agent.Key];
                if(agents.ContainsKey(agent.Key)){
                agents[agent.Key].GetComponent<MatrixMovement>().SetMovement(previousPosition, currentPosition, timeToUpdate);
                }
                
            }

            foreach(StreetLightData lightData in streetLightData.positions)
            {
                if (streetLights.ContainsKey(lightData.id))
                {
                    streetLights[lightData.id].GetComponent<StreetLight>().SetState(lightData.state);
                }
            }
        }
    }
 
    IEnumerator UpdateSimulation()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + updateEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            StartCoroutine(GetAgentsData());
            StartCoroutine(GetTrafficLightData());
        }
    }

    IEnumerator SendConfiguration()
    {
        /*
        The SendConfiguration method is used to send the configuration to the server.

        It uses a WWWForm to send the data to the server, and then it uses a UnityWebRequest to send the form.
        */
        WWWForm form = new WWWForm();

        form.AddField("NAgents", NAgents.ToString());
        form.AddField("width", width.ToString());
        form.AddField("height", height.ToString());

        UnityWebRequest www = UnityWebRequest.Post(serverUrl + sendConfigEndpoint, form);
        www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            // Once the configuration has been sent, it launches a coroutine to get the agents data.
            StartCoroutine(GetAgentsData());
            StartCoroutine(GetObstacleData());
            StartCoroutine(GetTrafficLightData());
            StartCoroutine(GetRoadData());
            StartCoroutine(GetDestinationData());
        }
    }

    IEnumerator GetAgentsData() 
    {
        // The GetAgentsData method is used to get the agents data from the server.

        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getAgentsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            // Once the data has been received, it is stored in the agentsData variable.
            // Then, it iterates over the agentsData.positions list to update the agents positions.
            agentsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            foreach(AgentData agent in agentsData.positions)
            {
                Vector3 newAgentPosition = new Vector3(agent.x, agent.y, agent.z);
                if(agents.ContainsKey(agent.id)){
                    Vector3 currentPosition = new Vector3();
                    if(currPositions.TryGetValue(agent.id, out currentPosition))
                        prevPositions[agent.id] = currentPosition;
                    currPositions[agent.id] = newAgentPosition;
                }
                else{
                    prevPositions[agent.id] = newAgentPosition;
                    agents[agent.id] = Instantiate(agentPrefab, new Vector3(0,0,0) , Quaternion.identity);
                }
                //Delete agents that are not in the list agents
                List<string> keysToRemove = new List<string>();
                foreach(var agentId in new List<string>(agents.Keys))
                {
                    if(!agentsData.positions.Exists(x => x.id == agentId))
                    {
                        keysToRemove.Add(agentId);
                    }
                }

                foreach (string key in keysToRemove)
                {
                    if (agents.TryGetValue(key, out GameObject carAgent))
                    {
                        // Check if the GameObject has a MatrixMovement component
                        MatrixMovement matrixMovement = carAgent.GetComponent<MatrixMovement>();
                        if (matrixMovement != null)
                        {
                            matrixMovement.DeleteCar();
                            agents.Remove(key);
                        }
                    }
                }
            }
            updated = true;
            if(!started) started = true;
        }
    }

    IEnumerator GetObstacleData() 
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getObstaclesEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            obstacleData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            foreach(AgentData obstacle in obstacleData.positions)
            {
                Instantiate(obstaclePrefab, new Vector3(obstacle.x, obstacle.y, obstacle.z), Quaternion.identity);
            }
        }
    }

    IEnumerator GetTrafficLightData() 
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getTrafficLightsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            streetLightData = JsonUtility.FromJson<StreetLightsData>(www.downloadHandler.text);

            foreach(StreetLightData trafficLight in streetLightData.positions)
            {
                if (!streetLights.ContainsKey(trafficLight.id))
                {
                    streetLights[trafficLight.id] = Instantiate(trafficlightPrefab, new Vector3(trafficLight.x, trafficLight.y, trafficLight.z), Quaternion.identity);
                    Instantiate(roadPrefab, new Vector3(trafficLight.x, trafficLight.y, trafficLight.z), Quaternion.identity);
                }
                else
                {
                    streetLights[trafficLight.id].GetComponent<StreetLight>().SetState(trafficLight.state);
                }
            }
        }
    }

    IEnumerator GetRoadData() 
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getRoadsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            roadData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);
            foreach(AgentData road in roadData.positions)
            {
                Instantiate(roadPrefab, new Vector3(road.x, road.y, road.z), Quaternion.identity);
            }
        }
    }

    IEnumerator GetDestinationData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getDestinationsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            destinationData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);
            foreach(AgentData destination in destinationData.positions)
            {
                Instantiate(destinationPrefab, new Vector3(destination.x,destination.y,destination.z), Quaternion.identity);
            }
        }
    }
}
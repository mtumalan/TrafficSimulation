using System.Collections;
using System.Collections.Generic;
using UnityEngine;


public class MatrixMovement : MonoBehaviour
{
    [Header("Car")]
    [SerializeField] Vector3 carScale;

    [Header("Wheels")]
    [SerializeField] Vector3 wheelScale;
    [SerializeField] GameObject wheelPrefab;
    [SerializeField] List<Vector3> wheels;

    [Header("Movement Interpolation")]
    [SerializeField] Vector3 startPosition = new Vector3(0, 0, 0);
    [SerializeField] Vector3 stopPosition = new Vector3(0, 0, 0);

    Mesh mesh;
    Vector3[] baseVertices;
    Vector3[] newVertices;
    List<Mesh> wheelMesh;
    List<Vector3[]> baseWheelVertices;
    List<Vector3[]> newWheelVertices;

    private List<GameObject> wheelObjects = new List<GameObject>();
    private float dt = 0;
    private float elapsedTime = 0;
    private float movementTime = 0;

    void Start()
    {
        // Get the mesh of the car and the wheels
        mesh = GetComponentInChildren<MeshFilter>().mesh;
        baseVertices = mesh.vertices;
        newVertices = new Vector3[baseVertices.Length];
        wheelMesh = new List<Mesh>();
        baseWheelVertices = new List<Vector3[]>();
        newWheelVertices = new List<Vector3[]>();

        // Set the time it takes to move from one point to another
        elapsedTime = movementTime;

        // Create the wheels
        foreach (Vector3 wheelPosition in wheels)
        {
            GameObject wheel = Instantiate(wheelPrefab, new Vector3(0,0,0), Quaternion.identity);
            wheelObjects.Add(wheel);
        }

        // Get the mesh of the wheels
        for (int i = 0; i < wheelObjects.Count; i++)
        {
            wheelMesh.Add(wheelObjects[i].GetComponentInChildren<MeshFilter>().mesh);
            baseWheelVertices.Add(wheelMesh[i].vertices);
            newWheelVertices.Add(new Vector3[baseWheelVertices[i].Length]);
        }
    }

    Vector3 SetNewTarget(Vector3 newTarget)
    {
        // If the new target is different from the current target, set the new target
        if(!this.stopPosition.Equals(newTarget))
        {
            startPosition = stopPosition;
            stopPosition = newTarget;
            dt = Mathf.Clamp(dt, 0, 1);
            Vector3 intPosition = Vector3.Lerp(startPosition, stopPosition, dt);
            return intPosition;
        } else { // If the new target is the same as the current target, return the current target
            return newTarget;
        }
    }

    // Delete the car and its wheels
    public void DeleteCar()
    {
        foreach (GameObject wheel in wheelObjects)
        {
            Destroy(wheel);
        }
        Destroy(this.gameObject);
    }

    void Update(){
        if(elapsedTime < 0) // If the car has reached its target, reset the time
        {
            elapsedTime = movementTime;

        }else
        {
            elapsedTime -= Time.deltaTime; // Update the time
            dt = 1.0f - (elapsedTime / movementTime); // Calculate the percentage of the time that has passed
        }
    }

    public void SetMovement(Vector3 newTarget, float movementTime){
        // Set the new target and the time it takes to move from one point to another
        Vector3 newPosition = SetNewTarget(newTarget);
        this.movementTime = movementTime;
        CarTransform(CarT(newPosition)); // Transform the car
        for (int i = 0; i < wheelObjects.Count; i++)
        {
            WheelTransform(WheelT(CarT(newPosition), i), i); // Transform the wheels
        }
    }

    Matrix4x4 CarT(Vector3 position){
        // Create the transformation matrices
        Matrix4x4 moveObject = HW_Transforms.TranslationMat(position.x,
                                                            position.y,
                                                            position.z);

        Matrix4x4 scale = HW_Transforms.ScaleMat(carScale.x, carScale.y, carScale.z);

        if (position.x != 0) // If the car is moving in the x axis, rotate it
        {
            float angle = Mathf.Atan2(stopPosition.x - startPosition.x, stopPosition.z - startPosition.z) * Mathf.Rad2Deg;
            Matrix4x4 rotate = HW_Transforms.RotateMat(angle, AXIS.Y);
            Matrix4x4 composite = moveObject * rotate * scale;
            return composite;
        }
        else
        { // If the car is moving just in the z axis, don't rotate it
            Matrix4x4 composite = moveObject * scale;
            return composite;
        }
    }

    Matrix4x4 WheelT(Matrix4x4 carComposite, int wheelIndex)
    {
        // Create the transformation matrices
        Matrix4x4 scale = HW_Transforms.ScaleMat(wheelScale.x, wheelScale.y, wheelScale.z);
        Matrix4x4 spawnRotate = HW_Transforms.RotateMat(90, AXIS.Y);
        Matrix4x4 rotate = HW_Transforms.RotateMat(-90 * Time.time, AXIS.X);
        Matrix4x4 move = HW_Transforms.TranslationMat(wheels[wheelIndex].x, 
                                                      wheels[wheelIndex].y, 
                                                      wheels[wheelIndex].z);
        Matrix4x4 composite = carComposite * move * rotate * spawnRotate * scale;
        return composite;
    }

    void CarTransform(Matrix4x4 carComposite)
    {
        // Transform the car
        for (int i = 0; i < newVertices.Length; i++)
        {
            Vector4 temp = new Vector4(baseVertices[i].x,
                                       baseVertices[i].y,
                                       baseVertices[i].z,
                                       1);
            newVertices[i] = carComposite * temp;
        }
        mesh.vertices = newVertices;
        mesh.RecalculateNormals();
        mesh.RecalculateBounds();
    }

    void WheelTransform(Matrix4x4 wheelComposite, int wheelIndex)
    {
        // Transform the wheels
        for (int j = 0; j < newWheelVertices[wheelIndex].Length; j++)
        {
            Vector4 temp = new Vector4(baseWheelVertices[wheelIndex][j].x,
                                        baseWheelVertices[wheelIndex][j].y,
                                        baseWheelVertices[wheelIndex][j].z,
                                        1);
            newWheelVertices[wheelIndex][j] = wheelComposite * temp;
        }

        wheelMesh[wheelIndex].vertices = newWheelVertices[wheelIndex];
        wheelMesh[wheelIndex].RecalculateNormals();
        wheelMesh[wheelIndex].RecalculateBounds();
    }
}
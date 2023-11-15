using System.Collections;
using System.Collections.Generic;
using UnityEngine;


public class MatrixMovement : MonoBehaviour
{
    [Header("Car Movement")]
    [SerializeField] Vector3 speed;
    [SerializeField] Vector3 carScale;

    [Header("Wheels")]
    [SerializeField] Vector3 wheelScale;
    [SerializeField] GameObject wheelPrefab;
    [SerializeField] List<Vector3> wheels;

    [Header("Movement Interpolation")]
    [SerializeField] Vector3 StartPosition;
    [SerializeField] Vector3 StopPosition;
    [SerializeField] float MotionTime;
    [SerializeField] List<Vector3> Waypoints;

    Mesh mesh;
    Vector3[] baseVertices;
    Vector3[] newVertices;
    List<Mesh> wheelMesh;
    List<Vector3[]> baseWheelVertices;
    List<Vector3[]> newWheelVertices;

    private List<GameObject> wheelObjects = new List<GameObject>();

    void Start()
    {
        mesh = GetComponentInChildren<MeshFilter>().mesh;
        baseVertices = mesh.vertices;
        newVertices = new Vector3[baseVertices.Length];
        wheelMesh = new List<Mesh>();
        baseWheelVertices = new List<Vector3[]>();
        newWheelVertices = new List<Vector3[]>();

        foreach (Vector3 wheelPosition in wheels)
        {
            GameObject wheel = Instantiate(wheelPrefab, new Vector3(0,0,0), Quaternion.identity);
            wheelObjects.Add(wheel);
        }

        for (int i = 0; i < wheelObjects.Count; i++)
        {
            wheelMesh.Add(wheelObjects[i].GetComponentInChildren<MeshFilter>().mesh);
            baseWheelVertices.Add(wheelMesh[i].vertices);
            newWheelVertices.Add(new Vector3[baseWheelVertices[i].Length]);
        }
    }

    // Update is called once per frame
    void Update(){
        CarTransform(CarT());
        for (int i = 0; i < wheelObjects.Count; i++){
            WheelTransform(WheelT(CarT(), i), i);
        }
    }

    Matrix4x4 CarT(){
        Matrix4x4 moveObject = HW_Transforms.TranslationMat(speed.x * Time.time,
                                                            speed.y * Time.time,
                                                            speed.z * Time.time);
        if (speed.x != 0){
            float angle = Mathf.Atan2(-speed.x, speed.z) * Mathf.Rad2Deg;
            Matrix4x4 rotate = HW_Transforms.RotateMat(angle, AXIS.Y);
            Matrix4x4 composite = moveObject * rotate;
            return composite;
        }
        else{
            Matrix4x4 composite = moveObject;
            return composite;
        }
    }
    Matrix4x4 WheelT(Matrix4x4 carComposite, int wheelIndex)
    {
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
    }

    void WheelTransform(Matrix4x4 wheelComposite, int wheelIndex)
    {
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
    }
}
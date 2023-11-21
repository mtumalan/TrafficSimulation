using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CarMovement : MonoBehaviour
{
    //Get wheel prefab
    [SerializeField] GameObject wheel;
    //Car initial position
    [SerializeField] Vector3 initialCarPosition;
    //Wheel offsets
    [SerializeField] Vector3 wheel1Offset = new Vector3(0, 0, 1);
    [SerializeField] Vector3 wheel2Offset = new Vector3(0, 0, -1);
    [SerializeField] Vector3 wheel3Offset = new Vector3(1, 0, 0);
    [SerializeField] Vector3 wheel4Offset = new Vector3(-1, 0, 0);

    // Set angle for wheels
    [SerializeField] Vector3 wheelRotation = new Vector3(0, 90, 0);

    // Set displacement vector
    [SerializeField] Vector3 displacement = new Vector3(0, 0, 1);

    // Set angle
    [SerializeField] float angle;

    // Car rotation axis
    [SerializeField] AXIS rotationAxis;

    Mesh mesh;
    Vector3[] baseVertices;
    Vector3[] newVertices;

    GameObject wheel1;
    GameObject wheel2;
    GameObject wheel3;
    GameObject wheel4;

    void Start()
    {
        // Set the initial position of the CarMovement GameObject
        initialCarPosition = transform.position;

        // Get the mesh component of the car
        mesh = GetComponentInChildren<MeshFilter>().mesh;

        // Get the vertices of the mesh
        baseVertices = mesh.vertices;

        // Create a new array to store the transformed vertices
        newVertices = new Vector3[baseVertices.Length];

        // Instantiate the wheels
        wheel1 = Instantiate(wheel, transform.position, Quaternion.Euler(wheelRotation));
        wheel2 = Instantiate(wheel, transform.position, Quaternion.Euler(wheelRotation));
        wheel3 = Instantiate(wheel, transform.position, Quaternion.Euler(wheelRotation));
        wheel4 = Instantiate(wheel, transform.position, Quaternion.Euler(wheelRotation));
    }

    // Update is called once per frame
    void Update()
    {
        DoTransform();
    }

    //Function that transforms the car's vertices depending on the time and the values of the displacement and angle vectors
    void DoTransform(){
        //Create matrixes
        Matrix4x4 move = HW_Transforms.TranslationMat(displacement.x*Time.time,
                                                      displacement.y*Time.time,
                                                      displacement.z*Time.time);

        Matrix4x4 moveOrigin = HW_Transforms.TranslationMat(-displacement.x, 
                                                           -displacement.y, 
                                                           -displacement.z);

        Matrix4x4 moveObject = HW_Transforms.TranslationMat(displacement.x, 
                                                           displacement.y, 
                                                           displacement.z);

        Matrix4x4 rotate = HW_Transforms.RotateMat(angle * Time.time,
                                                   rotationAxis);  

        //Combine matrixes
        Matrix4x4 composite = moveObject*rotate*moveOrigin;

        for (int i = 0; i<newVertices.Length; i++){
            Vector4 temp = new Vector4(baseVertices[i].x,
                                       baseVertices[i].y,
                                       baseVertices[i].z,
                                       1);
            newVertices[i] = composite * temp;
        }
        mesh.vertices = newVertices;
        mesh.RecalculateNormals();
    }
}
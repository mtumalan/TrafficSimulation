using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ApplyTransform : MonoBehaviour
{
    [SerializeField] Vector3 displacement;
    [SerializeField] float angle;
    [SerializeField] AXIS rotationAxis;

    Mesh mesh;
    Vector3[] baseVertices;
    Vector3[] newVertices;
    void Start(){
        mesh = GetComponentInChildren<MeshFilter>().mesh;
        baseVertices = mesh.vertices;

        newVertices = new Vector3[baseVertices.Length];
        for (int i = 0; i < baseVertices.Length; i++){
            newVertices[i] = baseVertices[i];
        }
    }

    void Update(){
        DoTransform();
    }

    void DoTransform(){
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
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class StreetLight : MonoBehaviour
{
    public void SetState(bool state){
        if(state){
            this.GetComponentInChildren<Light>().color = Color.green;
        }else{
            this.GetComponentInChildren<Light>().color = Color.red;
        }
    }
}

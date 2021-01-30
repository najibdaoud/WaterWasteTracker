#!/usr/bin/env python3
print("IMPORTING ONSHAPE CLIENT..")
from onshape_client.client import Client
from ev3dev2.sensor.lego import UltrasonicSensor, GyroSensor
from ev3dev2.button import Button
import time
import json


btn = Button()
us = UltrasonicSensor()
gs = GyroSensor()
gs.calibrate()


isButton = False
isWater = False
isObject = False
waterTimeElapsed = 0.0
objectTimeElapsed = 0.0
waterStart = 0.0
waterStop = 0.0
objectStart = 0.0
objectStop = 0.0
time.sleep(3)

print("WATER TRACKING BEGINNING..")
while isButton == False:
    angle = gs.value()
    dist = us.value()

    # print(angle)
    # print(dist)

    
    if (angle > 20):
        if isWater == False:
            print("WATER IS ON")
            waterStart = time.time()
            isWater = True
        
        if (dist < 250):
            if isObject == False:
                print("OBJECT IS THERE")
                objectStart = time.time()
                isObject = True
        else:
            if isObject == True:
                print("OBJECT IS NOT THERE")
                objectStop = time.time()
                objectTimeElapsed += objectStop - objectStart
                print("object: ")
                print(objectTimeElapsed)
                isObject = False
        
        time.sleep(1)
    else:
        if isWater == True:
            print("WATER IS OFF")
            waterStop = time.time()
            waterTimeElapsed += waterStop - waterStart
            print("water: ")
            print(waterTimeElapsed)
            isWater = False
            time.sleep(1)
    
    if (btn.any()):
        print("WATER TRACKING ENDING..\n")
        isButton = True
        waterStop = time.time()
        waterTimeElapsed += waterStop - waterStart
        time.sleep(1)


print("WATER RUNTIME TOTAL: ")
print(waterTimeElapsed)
print("WATER IN USE RUNTIME: ")
print(objectTimeElapsed)
print("WATER NOT IN USE RUNTIME: ")
print(waterTimeElapsed - objectTimeElapsed, "\n")

waterUsed = (objectTimeElapsed / waterTimeElapsed) * 100
print("WATER AMOUNT USED:")
print(round(waterUsed, 2), "%")
print("WATER AMOUNT WASTED:")
print(round(100 - waterUsed, 2), "%\n")
time.sleep(10)

print("SENDING DATA TO ONSHAPE..")

key = ""
secret = ""

with open("api_key", "r") as f:
	key = f.readline().rstrip()
	secret = f.readline().rstrip()

base_url = 'https://rogers.onshape.com'

client = Client(configuration={"base_url": base_url, "access_key": key, "secret_key": secret})

get_string = "/api/featurestudios/d/47ae61cd406728788f680ba5/w/ffaa0924f378e535b8076f3b/e/468bc7291ca6dee948504a04"
update_string = "/api/featurestudios/d/47ae61cd406728788f680ba5/w/ffaa0924f378e535b8076f3b/e/468bc7291ca6dee948504a04"
post_api_call = base_url + update_string
get_api_call = base_url + get_string


fs1 = """FeatureScript 1301;
	import(path : "onshape/std/geometry.fs", version : "1301.0");
	annotation { "Feature Type Name" : "Water Wasted" }
	export const myFeature = defineFeature(function(context is Context, id is Id, definition is map)
		precondition
		{
			// Define the parameters of the feature type
		}
		{	
            var sketch1 = newSketch(context, id + "sketch1", {
                "sketchPlane" : qCreatedBy(makeId("Top"), EntityType.FACE)
            });
            
            // Create sketch entities here
            skRectangle(sketch1, "rectangle1", {
                    "firstCorner" : vector(0, 0) * inch,
                    "secondCorner" : vector(2, 2) * inch
            });
            
            skSolve(sketch1);
            
            opExtrude(context, id + "extrude1", {
                "entities" : qSketchRegion(id + "sketch1", true),
                "direction" : evOwnerSketchPlane(context, {
                        "entity" : qSketchRegion(id + "sketch1", true)
                }).normal,
                "endBound" : BoundingType.BLIND,
                "endDepth" : """

fs2 = str(round(100 - waterUsed) / 10)

fs3 = """       * inch
            });
            // Define the function's action
            // Define the function's action
            // Define the function's action
    });"""

full_fs = fs1 + fs2 + fs3

# Make API Calls
headers = {'Accept': 'application/vnd.onshape.v1+json', 'Content-Type': 'application/json'}
r = client.api_client.request('GET', url=get_api_call, query_params={}, headers=headers)
result = json.loads(r.data)
# print(json.dumps(result, indent=2))

#Find rejectMicroversionSkew, serializationVersion, sourceMicroversion
serializationVersion = result["serializationVersion"]
sourceMicroversion = result["sourceMicroversion"]
rejectMicroversionSkew = result["rejectMicroversionSkew"]

body = {"contents": full_fs,
		"serializationVersion": str(serializationVersion), 
		"sourceMicroversion": str(sourceMicroversion),
		"rejectMicroversionSkew": str(rejectMicroversionSkew)}

r = client.api_client.request("POST", url=post_api_call, query_params={}, headers=headers, body=body)
result2 = json.loads(r.data)
# print(json.dumps(result2, indent=2))

print("DATA SENDING COMPLETE")
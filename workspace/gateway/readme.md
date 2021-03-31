# Tensorflow CI Client

This readme should explain the basic usage of the different files.

## Getting Started
For just starting the client the execution of the following command should get you started.

```
python3 client.py
```

## Running the components

### Client Classes

The is even a python library for just using the requests throuth a class.
The following cli commands in python are necessary to implement a basic use.

```
from client_class import *
detector = Detection()

print(cli_signature())
print("Model version: " + detector.model_version())
detector.request()
output_dict = detector.conversion()
detector.visualization()
detector.bounding_boxes()
```
the Detection class can be called in different ways. One is already showen. The other way would be to pass on the arguments for connecting the server.

```
server_url = 'http://172.28.1.3:8080/v1/models/default'
path_to_labelmap = '/tensorflow/workspace/training/annotations/label_map.pbtxt'
load_image = './dog.jpg'
output_image = './dog_detection_resault.jpg'
detector = Detection(server_url, label_map, image_path, output_image)
print(cli_signature())
print("Model version: " + detector.model_version())
detector.request()
output_dict = detector.conversion()
detector.visualization()
detector.bounding_boxes()
```
all of this parameters are strings and are a part of the server settings of the tf serving.

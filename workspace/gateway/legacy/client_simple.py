import PIL.Image
import numpy as np
import requests
import time
import json
from PIL import Image
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
from pprint import pprint

################ SERVER SETTINGS ################
host = "172.28.1.3"
port = "8080"
path_to_labelmap = "/tensorflow/workspace/training/annotations/label_map.pbtxt" #the absolute location where the label_map is.
load_image = "../dog.jpg"
output_image = "./dog_detection_resault.jpg" #under which name should the detection be saved
#################################################

# http://172.28.1.3:8080/v1/models/default:predict
# Detect used model version
res = requests.get("http://"+host+":"+port+"/v1/models/default")
req_model_version = json.loads(res.text)
model_versions = req_model_version["model_version_status"]
model_version_json = [obj for obj in model_versions if(obj['state'] == 'AVAILABLE')] 
print("Active model version:" + model_version_json[0]['version'])

# Make a prediction request
image = PIL.Image.open(load_image)  # Change dog.jpg with your image
image.show() # just show it
image_np = np.array(image)
payload = {"instances": [image_np.tolist()]}
start = time.perf_counter()
res = requests.post("http://"+host+":"+port+"/v1/models/default:predict", json=payload)
print(f"Took {time.perf_counter()-start:.2f}s")

# Cast json response
# pprint(res.json())
detection_boxes = res.json()["predictions"][0]["detection_boxes"]
detection_classes = res.json()["predictions"][0]["detection_classes"]
detection_scores = res.json()["predictions"][0]["detection_scores"]
output_dict = res.json()["predictions"][0]
output_dict['num_detections'] = int(output_dict['num_detections'])
output_dict['detection_classes'] = np.array([int(class_id) for class_id in output_dict['detection_classes']])
output_dict['detection_boxes'] = np.array(output_dict['detection_boxes'])
output_dict['detection_scores'] = np.array(output_dict['detection_scores'])
#write json to file
#with open('personal.json', 'w') as json_file:  
#json.dump(res.json(), json_file)

# Convert LabelMap
category_index = label_map_util.create_category_index_from_labelmap(path_to_labelmap, use_display_name=True)

# Visualization of the results of a detection.
vis_util.visualize_boxes_and_labels_on_image_array(
			image_np,
            output_dict['detection_boxes'],
            output_dict['detection_classes'],
            output_dict['detection_scores'],
            category_index,
            instance_masks=output_dict.get('detection_masks'),
            use_normalized_coordinates=True,
            line_thickness=8,
)
Image.fromarray(image_np).save("./dog_detection_resault.jpg")

print("end")

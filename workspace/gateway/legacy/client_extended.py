import PIL.Image
import numpy as np
import requests
import time
import json
import argparse
from PIL import Image
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
from pprint import pprint

################ SERVER SETTINGS ################
#host = "172.28.1.3"
#port = "8080"
#server_url =
#path_to_labelmap = "/tensorflow/workspace/training/annotations/label_map.pbtxt" #the absolute location where the label_map is.
#load_image = "./dog.jpg"
#output_image = "./dog_detection_resault.jpg" #under which name should the detection be saved
#################################################

def detection_version(server_url):
	# Detect used model version
	# GET http://172.28.1.3:8080/v1/models/default
	res = requests.get(server_url)
	req_model_version = json.loads(res.text)
	model_versions = req_model_version["model_version_status"]
	model_version_json = [obj for obj in model_versions if(obj['state'] == 'AVAILABLE')]
	return model_version_json[0]['version']

def detection_request(server_url):
	# Make a prediction request
	# POST http://172.28.1.3:8080/v1/models/default:predict
	image = PIL.Image.open(load_image)  # Change dog.jpg with your image
	image.show() # just show it
	image_np = np.array(image)
	payload = {"instances": [image_np.tolist()]}
	start = time.perf_counter()
	res = requests.post(server_url+":predict", json=payload)
	print("Detection request took: " + f"{time.perf_counter()-start:.2f}s")
	return res, image_np

def detection_conversion(res):
	# Convert Json response
	# pprint(res.json())
	detection_boxes = res.json()["predictions"][0]["detection_boxes"]
	detection_classes = res.json()["predictions"][0]["detection_classes"]
	detection_scores = res.json()["predictions"][0]["detection_scores"]
	output_dict = res.json()["predictions"][0]
	output_dict['num_detections'] = int(output_dict['num_detections'])
	output_dict['detection_classes'] = np.array([int(class_id) for class_id in output_dict['detection_classes']])
	output_dict['detection_boxes'] = np.array(output_dict['detection_boxes'])
	output_dict['detection_scores'] = np.array(output_dict['detection_scores'])
	# Write json to file
	#with open('personal.json', 'w') as json_file:  
	#json.dump(res.json(), json_file)
	return output_dict

def detection_visualization(image_np, output_dict):
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
	Image.fromarray(image_np).save(output_image)

def cli_signature():
	signature_cli = """
################################################################################################################################
################################################################################################################################
 __  __ ______      _______         _____                  _          _______      __          __  __ _                  _____ 
|  \/  |  _ \ \    / /  __ \       |  __ \                | |        |  __ \ \    / /\        |  \/  | |                / ____|
| \  / | |_) \ \  / /| |  | |______| |  | | ___  ___ _ __ | |  ______| |  | \ \  / /  \ ______| \  / | |     __ _  __ _| (___  
| |\/| |  _ < \ \/ / | |  | |______| |  | |/ _ \/ _ \ '_ \| | |______| |  | |\ \/ / /\ \______| |\/| | |    / _` |/ _` |\___ \ 
| |  | | |_) | \  /  | |__| |      | |__| |  __/  __/ |_) | |____    | |__| | \  / ____ \     | |  | | |___| (_| | (_| |____) |
|_|  |_|____/   \/   |_____/       |_____/ \___|\___| .__/|______|   |_____/   \/_/    \_\    |_|  |_|______\__,_|\__,_|_____/ 
                                                    | |                                                                        
                                                    |_|                                                                        
################################################################################################################################
####################################################### Version 1.0.          ##################################################
####################################################### Viktor Walter-Tscharf ##################################################
################################################################################################################################"""
	return signature_cli

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Performs call to the tensorflow-serving REST API.')
	parser.add_argument('--server_url', dest='server_url', type=str, default ='http://172.28.1.3:8080/v1/models/default',
                        help='URL of the tensorflow-serving accepting API call. '
                             'e.g. http://localhost:8501/v1/models/omr_500')
	parser.add_argument('--label_map', dest='label_map', type=str, default='/tensorflow/workspace/training/annotations/label_map.pbtxt',
                        help='Path to the label map, which is json-file that maps each category name '
                             'to a unique number.')
	parser.add_argument('--image_path', dest='image_path', type=str, default="./dog.jpg",
                        help='Path to the jpeg image')
	parser.add_argument('--output_image', dest='output_image', type=str, default='./dog_detection_resault.jpg',
                        help='Path to the output image file resulting from the API call')
	args = parser.parse_args()
	
	server_url = args.server_url
	path_to_labelmap = args.label_map
	load_image = args.image_path
	output_image = args.output_image

	print(cli_signature())
	print("Model version: " + detection_version(server_url))
	res, image_np = detection_request(server_url)
	output_dict = detection_conversion(res)
	detection_visualization(image_np, output_dict)




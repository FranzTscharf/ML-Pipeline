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

class Detection:

	def __init__(self, server_url, label_map, image_path, output_image):
		self.server_url = server_url
		self.path_to_labelmap = label_map
		self.load_image = image_path
		self.output_image = output_image
	def __init__(self): #test constructor
		self.server_url = 'http://172.28.1.3:8082/v1/models/default'
		self.path_to_labelmap = '/tensorflow/workspace/training/annotations/label_map.pbtxt'
		self.load_image = '/tensorflow/workspace/serving/client/public/uploads/input_img_document.jpg'
		self.output_image = '/tensorflow/workspace/serving/client/public/uploads/input_img_document_detection_results.jpg'
	def model_version(self):
		# Detect used model version
		# GET http://172.28.1.3:8080/v1/models/default
		res = requests.get(self.server_url)
		req_model_version = json.loads(res.text)
		model_versions = req_model_version["model_version_status"]
		model_version_json = [obj for obj in model_versions if(obj['state'] == 'AVAILABLE')]
		return model_version_json[0]['version']

	def request(self):
		# Make a prediction request
		# POST http://172.28.1.3:8080/v1/models/default:predict
		image = PIL.Image.open(self.load_image)  # Change dog.jpg with your image
		image.show() # just show it
		image_np = np.array(image)
		image.close()
		payload = {"instances": [image_np.tolist()]}
		start = time.perf_counter()
		res = requests.post(self.server_url+":predict", json=payload)
		print("Detection request took: " + f"{time.perf_counter()-start:.2f}s")
		self.res = res
		self.image_np = image_np

	def conversion(self):
		# Convert Json response
		# pprint(res.json())
		output_dict = self.res.json()["predictions"][0]
		output_dict['num_detections'] = int(output_dict['num_detections'])
		output_dict['detection_classes'] = np.array([int(class_id) for class_id in output_dict['detection_classes']])
		output_dict['detection_boxes'] = np.array(output_dict['detection_boxes'])
		output_dict['detection_scores'] = np.array(output_dict['detection_scores'])
		# Write json to file
		#with open('personal.json', 'w') as json_file:  
		#json.dump(res.json(), json_file)
		self.output_dict = output_dict

	def visualization(self):
		# Convert LabelMap
		category_index = label_map_util.create_category_index_from_labelmap(self.path_to_labelmap, use_display_name=True)
		# Visualization of the results of a detection.
		vis_util.visualize_boxes_and_labels_on_image_array(
				self.image_np,
	            self.output_dict['detection_boxes'],
	            self.output_dict['detection_classes'],
	            self.output_dict['detection_scores'],
	            category_index,
	            instance_masks=self.output_dict.get('detection_masks'),
	            use_normalized_coordinates=True,
	            line_thickness=8,
		)
		Image.fromarray(self.image_np).save(self.output_image)

	def bounding_boxes(self):
		image = Image.open(self.load_image)
		image_width, image_height = image.size
		image.close()
		category_index = label_map_util.create_category_index_from_labelmap(self.path_to_labelmap, use_display_name=True)
		boxes = self.output_dict['detection_boxes']
		classes = self.output_dict['detection_classes']
		scores = self.output_dict['detection_scores']
		boxes_list = []
		for index, scores in enumerate(scores):
			if scores > 0.5:
				ymin, xmin, ymax, xmax = boxes[index]
				label = category_index[classes[index]]['name']
				boxes_entry = []
				boxes_entry.append(label)
				boxes_entry.append(scores)
				boxes_entry.append(int(xmin * image_width))			
				boxes_entry.append(int(ymin * image_height))
				boxes_entry.append(int(xmax * image_width))
				boxes_entry.append(int(ymax * image_height))
				boxes_list.append(boxes_entry)
				#boxes_entry = label, scores, int(xmin * image_width), int(ymin * image_height), int(xmax * image_width), int(ymax * image_height)
				#boxes_list = list(label, scores, int(xmin * image_width), int(ymin * image_height), int(xmax * image_width), int(ymax * image_height))
				boxes_list.append(boxes_entry)
			else:
				continue
		self.boxes_list = boxes_list
		print(self.boxes_list)

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
	####################################################### Version 1.0.0         ##################################################
	####################################################### Viktor Walter-Tscharf ##################################################
	################################################################################################################################"""
		return signature_cli

def test():
	#definitions
	#server_url = args.server_url
	#path_to_labelmap = args.label_map
	#load_image = args.image_path
	#output_image = args.output_image
	detector = Detection()

	print(cli_signature())
	print("Model version: " + detector.model_version())
	detector.request()
	detector.conversion()
	detector.visualization()
	detector.bounding_boxes()

	
if __name__ == '__main__':
	test()




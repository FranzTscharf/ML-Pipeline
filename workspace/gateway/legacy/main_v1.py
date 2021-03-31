import PIL.Image
import numpy as np
import time
import json
import argparse
import os
import time
import io
import requests
import datetime
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from PIL import Image
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
from pprint import pprint
from flask import Flask, render_template, jsonify, send_file
from flask_restplus import Api, Resource, reqparse
from werkzeug.datastructures import FileStorage
from pdf2image import convert_from_path, convert_from_bytes
from shutil import copyfile

app = Flask(__name__)
api = Api(app, version='alpha 0.1.4', title='MBVD-DeepL-DVA-MLaaS-API',description='An Swagger UI and API for tf serving and ci of new models. The models are based on user feedback.',)

ns_conf = api.namespace('rbci', description='This endpoints is for the region based content identification.')
detector = None
@ns_conf.route("/tfservingendpoint")
class TFServingEndpoint(Resource):
	def get(self):
		response = {}
		response['server_url'] = detector.server_url
		response['path_to_labelmap'] = detector.path_to_labelmap
		response['load_image'] = detector.load_image
		response['output_image'] = detector.output_image
		return response
@ns_conf.route("/listofmodels")
class ModelsList(Resource):
	def get(self):
		return detector.model_versions()
@ns_conf.route("/modelversion")
class Modelversion(Resource):
	def get(self):
		return detector.model_version()
img_parser = reqparse.RequestParser()
img_parser.add_argument('json', type=list, required=False, location='json', help='{"img_name":"input_img_document.jpg"}')#, defaults={'latitude':123, 'longitude': 56})
@ns_conf.route("/detecttoarray")
@ns_conf.expect(img_parser)
class DetectToArray(Resource):
	def post(self):
		try:
			args = img_parser.parse_args()
			#jsonObj = json.loads(str(args['json']))
			#print(args['json'])
			#img_name = jsonObj['img_name']
			#if img_name == 'input_img_document.jpg':
			#	img_path = detector.load_image
			#else:
			#	img_path = os.path.join(detector.output_image, img_name)
			#print(img_name)
			detector.request()
			detector.conversion()
			return detector.bounding_boxes()
		except Exception as e:
			return e, 500
@ns_conf.route("/detecttoimage")
class DetectToImage(Resource):
	def get(self):
		tmpFileName = "img_result_"+datetime.datetime.now().strftime("%Y-%m-%d%H-%M-%s")+".jpg"
		detector = Detection()
		detector.request()
		detector.conversion()
		detector.visualization(tmpFileName)
		return send_file(
	        str(detector.output_image) + tmpFileName,
	        as_attachment=True,
	        mimetype='image/png')
ns_conf = api.namespace('upload', description='This endpoints is for uploading documents to the content server')
upload_parser = reqparse.RequestParser()
upload_parser.add_argument('file', location='files', type=FileStorage, required=True)
@ns_conf.route("/img")
@ns_conf.expect(upload_parser)
class UploadImage(Resource):
	def post(self):
		args = upload_parser.parse_args()
		uploaded_file = args['file']  # This is FileStorage instance
		if uploaded_file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
			tmpFileName = "img_"+datetime.datetime.now().strftime("%Y-%m-%d%_H-%M-%s")+".jpg" #get randome name for not dobble save etc.
			tmpPath = str(detector.output_image) + tmpFileName
			uploaded_file.save(tmpPath) # save image for backup and later usage
			copyfile(tmpPath, detector.load_image) # make a copy of the image to the detection folder
			#url = do_something_with_file(uploaded_file)
			return {'filename': uploaded_file.filename, 'upload': True, 'img_name':tmpFileName,'img_path': tmpPath}, 201
		else:
			return {'filename': uploaded_file.filename, 'upload': False, 'comment': 'wrong file format'}, 415 
@ns_conf.route("/pdf")
@ns_conf.expect(upload_parser)
class UploadPDF(Resource):
	def post(self):
		args = upload_parser.parse_args()
		uploaded_file = args['file']  # This is FileStorage instance
		if uploaded_file.filename.lower().endswith('.pdf'):
			tmpTime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%s")
			tmpFileNamePDF = "document_"+tmpTime+".pdf"
			tmpPathPDF = str(detector.output_image) + tmpFileNamePDF
			uploaded_file.save(tmpPathPDF)
			tmpFileNameIMG = "img_"+tmpTime+".jpg"
			tmpPathIMG = str(detector.output_image) + tmpFileNameIMG
			images = convert_from_path(tmpPathPDF)
			# images[0] only take first page of pdf because we only do detection this one.
			images[0].save(tmpPathIMG, 'JPEG') # save to tmp folder
			images[0].save(detector.load_image, 'JPEG') # save to instance detect
			#url = do_something_with_file(uploaded_file)
			return {'filename': uploaded_file.filename, 'upload': True, 'pdf_name':tmpFileNamePDF,'pdf_path': tmpPathPDF, 'img_name':tmpFileNameIMG,'img_path':tmpPathIMG}, 201
		else:
			return {'filename': uploaded_file.filename, 'upload': False, 'comment': 'wrong file format'}, 415

ns_conf = api.namespace('ocr', description='This endpoints is for the communication with the tesseract ocr engine.')
@ns_conf.route("/version")
class version(Resource):
	def get(self):
		return False

#class implementaiton
class Detection:
	def __init__(self, server_url, label_map, image_path, output_image):
		"""
		Custom constructor
		:param server_url:
		:param label_map:
		:param image_path:
		:param output_image:
		"""
		self.server_url = server_url
		self.path_to_labelmap = label_map
		self.load_image = image_path
		self.output_image = output_image
	def __init__(self):
		"""
		Default constructor
		"""
		self.server_url = 'http://172.28.1.3:8082/v1/models/default'
		self.path_to_labelmap = '/tensorflow/workspace/pipeline/configs/label_map.pbtxt'
		self.load_image = '/tensorflow/workspace/gateway/public/uploads/input_img_document.jpg'
		self.output_image = '/tensorflow/workspace/gateway/public/tmp/'
	def model_version(self):
		"""
		Detect used model version
		GET http://172.28.1.3:8080/v1/models/default
		:return: models
		"""
		res = requests_retry_session().get(self.server_url)
		#res = requests.get(self.server_url)
		req_model_version = json.loads(res.text)
		model_versions = req_model_version["model_version_status"]
		model_version_json = [obj for obj in model_versions if(obj['state'] == 'AVAILABLE')]
		return model_version_json[0]['version']
	def model_versions(self):
		"""
		Detect used model version
		GET http://172.28.1.3:8080/v1/models/default
		:return:
		"""
		res = requests_retry_session().get(self.server_url)
		req_model_version = json.loads(res.text)
		return req_model_version
	def request(self):
		"""
		Make a prediction request
		POST http://172.28.1.3:8080/v1/models/default:predict
		:return:
		"""
		image = PIL.Image.open(self.load_image)  # !TODO Change dog.jpg with your image
		#image.show() # just show it
		image_np = np.array(image)
		image.close()
		payload = {"instances": [image_np.tolist()]}
		start = time.perf_counter()
		res = requests_retry_session().post(self.server_url+":predict", json=payload)
		print("Detection request took: " + f"{time.perf_counter()-start:.2f}s")
		self.res = res
		self.image_np = image_np
	def conversion(self):
		"""
		Convert Json response
		pprint(res.json())
		:return:
		"""
		output_dict = self.res.json()["predictions"][0]
		output_dict['num_detections'] = int(output_dict['num_detections'])
		output_dict['detection_classes'] = np.array([int(class_id) for class_id in output_dict['detection_classes']])
		output_dict['detection_boxes'] = np.array(output_dict['detection_boxes'])
		output_dict['detection_scores'] = np.array(output_dict['detection_scores'])
		# Write json to file
		#with open('personal.json', 'w') as json_file:  
		#json.dump(res.json(), json_file)
		self.output_dict = output_dict
	def visualization(self, tmpFileName):
		"""
		Visualization of bounding boxes
		:param tmpFileName:
		:return:
		"""
		# Convert LabelMap
		category_index = label_map_util.create_category_index_from_labelmap(self.path_to_labelmap, use_display_name=True)
		boxes = self.output_dict['detection_boxes'] # get 
		classeslist = self.output_dict['detection_classes']
		scoreslist = self.output_dict['detection_scores']
		# Visualization of the results of a detection.
		vis_util.visualize_boxes_and_labels_on_image_array(
				self.image_np,
	            boxes,
	            classeslist,
	            scoreslist,
	            category_index,
	            instance_masks=self.output_dict.get('detection_masks'),
	            use_normalized_coordinates=True,
	            line_thickness=8,
		)
		Image.fromarray(self.image_np).save(str(self.output_image)+tmpFileName)
	def bounding_boxes(self):
		"""
		Convert bounding boxes to response
		:return:
		"""
		image = Image.open(self.load_image)
		image_width, image_height = image.size
		image.close()
		category_index = label_map_util.create_category_index_from_labelmap(self.path_to_labelmap, use_display_name=True)
		boxes = self.output_dict['detection_boxes'] # get 
		classes = self.output_dict['detection_classes']
		scores = self.output_dict['detection_scores']
		boxes_list = []
		for index, scores in enumerate(scores):
			if scores > 0.5 and not category_index[classes[index]]['name'] in str(boxes_list): # The first filters classer lower then 50% detection. The secend checks if the class is already detected with a higher score(remove doublicates)
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
				#boxes_list.append(boxes_entry)
			else:
				continue
		self.boxes_list = boxes_list
		return self.boxes_list
	def cli_signature(self):
		"""
		Print signature
		:return: string
		"""
		return ""
def requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None):
	"""
	Implementation of retry of http request if failture
	:param retries:
	:param backoff_factor:
	:param status_forcelist:
	:param session:
	:return:
	"""
	session = session or requests.Session()
	retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
	adapter = HTTPAdapter(max_retries=retry)
	session.mount('http://', adapter)
	session.mount('https://', adapter)
	return session
	
if __name__ == '__main__':
	detector = Detection()
	#print(detector.cli_signature())
	#time.sleep(1)
	app.run(host='0.0.0.0', port=5000,debug=True)
	# init detector



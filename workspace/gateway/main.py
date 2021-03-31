import PIL.Image, numpy as np, time, json, argparse, os, time, io, requests, datetime
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from PIL import Image
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
from pprint import pprint
from flask import Flask, render_template, jsonify, send_file
from flask_restplus import Api, Resource, reqparse
from werkzeug.utils import cached_property
from werkzeug.datastructures import FileStorage
from pdf2image import convert_from_path, convert_from_bytes
from shutil import copyfile
import werkzeug
import csv

############## SETTINGS ##################
static_folder = '/tensorflow/workspace/gateway/public/' # path to the public folder of the gateway server
pipeline_api_url = 'http://172.28.1.5:8090/api/' # the url of apache airflow api. This is the Pipeline component
csv_input = '/tensorflow/workspace/gateway/public/config/annotations.csv'  # path of the annotations.csv
tmp_image_path = '/tensorflow/workspace/gateway/public/tmp/' #path to the tmp folder of the images
train_data_path = '/tensorflow/workspace/gateway/public/data/' #path to the folder of the images used for the next training
##########################################

app = Flask(__name__,static_folder=static_folder)
api = Api(app, version='alpha 0.1.14', title='MBVD-DeepLearning-DVA-MLaaS-API',description='An Swagger UI and API for tf serving and ci of new models. The models are based on user feedback.',)

ns_conf = api.namespace('pipeline', description='This endpoints is for the communication of the pipeline service.')
@ns_conf.route("/status")
class PipelineStatus(Resource):
	def get(self):
		pipeline_server_url = pipeline_api_url + "experimental/test"
		res = requests_retry_session().get(pipeline_server_url)
		return jsonify(res.text)
@ns_conf.route("/lastRun")
class LastRun(Resource):
	def get(self):
		pipeline_server_url = pipeline_api_url + "experimental/latest_runs"
		res = requests_retry_session().get(pipeline_server_url)
		return jsonify(res.text)
@ns_conf.route("/activate")
class Activate(Resource):
	def get(self):
		pipeline_server_url = pipeline_api_url + "experimental/dags/main/paused/false"
		res = requests_retry_session().get(pipeline_server_url)
		return jsonify(res.text)
@ns_conf.route("/deactivate")
class Deactivate(Resource):
	def get(self):
		pipeline_server_url = pipeline_api_url + "experimental/dags/main/paused/true"
		res = requests_retry_session().get(pipeline_server_url)
		return jsonify(res.text)
@ns_conf.route("/run")
class RunPipeline(Resource):
	def post(self):
		pipeline_server_url = pipeline_api_url + "experimental/dags/main/paused/false"
		res = requests_retry_session().get(pipeline_server_url)
		pipeline_server_url = "http://172.28.1.5:8090/api/experimental/dags/main/dag_runs"
		payload = "{\"conf\":\"{\\\"key\\\":\\\"value\\\"}\"}"
		headers = {
			'cache-control': "no-cache",
			'content-type': "application/json"
		}
		res = requests_retry_session().post(pipeline_server_url, data=payload, headers=headers)
		#response = requests.request("POST", url, data=payload, headers=headers)
		return jsonify(res.text)

ns_conf = api.namespace('serving', description='This endpoints is for the region based content identification.')
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
img_parser.add_argument('filename', type=str, default='input_img_document.jpg')
@ns_conf.route("/detecttoarray")
@ns_conf.expect(img_parser)
class DetectToArray(Resource):
	def get(self):
		try:
			try:
				args = img_parser.parse_args()
				img_name = str(args['filename'])
				if img_name.endswith(('.jpg','.JPEG','.JPG','.PNG','.png','.gif','.biff')):
					img_path = os.path.join(detector.output_image, img_name)
					#return img_path
					detector.request(img_path)
					detector.conversion()
					return detector.bounding_boxes(img_path)
				else:
					raise ValueError('it is not a picture')
			except Exception as e:
				return 500, "can't read filename"
			return img_path
		except Exception as e:
			return e, 500
img_parser = reqparse.RequestParser()
img_parser.add_argument('filename', type=str, default='input_img_document.jpg')
@ns_conf.route("/detecttoimage")
@ns_conf.expect(img_parser)
class DetectToImage(Resource):
	def get(self):
		try:
			try:
				args = img_parser.parse_args()
				img_name = str(args['filename'])
				if img_name.endswith(('.jpg','.JPEG','.JPG','.PNG','.png','.gif','.biff')):
					tmpFileName = "img_result_"+datetime.datetime.now().strftime("%Y-%m-%d%H-%M-%s")+".jpg"
					img_path = os.path.join(detector.output_image, img_name)
					#return img_path
					detector.request(img_path)
					detector.conversion()
					detector.visualization(tmpFileName)
					return send_file(str(detector.output_image) + tmpFileName, as_attachment=True, mimetype='image/png')
				else:
					raise ValueError('it is not a picture')
			except Exception as e:
				return 500, "can't read filename"
			return img_path
		except Exception as e:
			return e, 500
ns_conf = api.namespace('gateway', description='This endpoints is for uploading documents to the content server')
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
@ns_conf.route("/document")
@ns_conf.expect(upload_parser)
class UploadDocument(Resource):
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
		elif uploaded_file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
			tmpFileName = "img_"+datetime.datetime.now().strftime("%Y-%m-%d%_H-%M-%s")+".jpg" #get randome name for not dobble save etc.
			tmpPath = str(detector.output_image) + tmpFileName
			uploaded_file.save(tmpPath) # save image for backup and later usage
			copyfile(tmpPath, detector.load_image) # make a copy of the image to the detection folder
			#url = do_something_with_file(uploaded_file)
			return {'filename': uploaded_file.filename, 'upload': True, 'img_name':tmpFileName,'img_path': tmpPath}, 201
		else:
			return {'filename': uploaded_file.filename, 'upload': False, 'comment': 'wrong file format'}, 415
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
feedback_parser = reqparse.RequestParser()
feedback_parser.add_argument('json', location='form', required=True, help="The json data obj of the d3 frontend")
@ns_conf.route("/feedback")
@ns_conf.expect(feedback_parser)
class Feedback(Resource):
	def post(self):
		args = feedback_parser.parse_args()
		jsonText = args['json'] #get the json from the request
		data = json.loads(jsonText)
		for item in data:
			row = [item['filename'],int(item['imgWidth']),int(item['imgHeight']),item['label'].lower(),int(item['xmin']),int(item['ymin']),int(item['xmax']),int(item['ymax'])]
			#!TODO move file from tmp to data folder
			with open(csv_input, 'a') as c:
				writer = csv.writer(c)
				writer.writerow(row)
			c.close()
			print("Key: " + str(item))
		return data
ns_conf = api.namespace('ocr', description='This endpoints is for the communication with the tesseract ocr engine.')
@ns_conf.route("/version")
class Version(Resource):
	def get(self):
		ocr_server_url = "http://172.28.1.6:7000/api"
		res = requests_retry_session().get(ocr_server_url)
		return {'version': str(res.text)}
roitext_parser = reqparse.RequestParser()
roitext_parser.add_argument('filename', location='form', required=True, help="The filenme of the image of the roi")
roitext_parser.add_argument('json', location='form', required=True, help="The json response of the detecttoarray endpoint")
@ns_conf.route("/roiToText")
@ns_conf.expect(roitext_parser)
class RoiToText(Resource):
	def post(self):
		ocr_server_url = "http://172.28.1.6:7000/api/convert"
		args = roitext_parser.parse_args()
		img_name = str(args['filename'])  # Get the file obj which is the FileStorage instance
		jsonText = args['json'] #get the json from the request
		print(jsonText)
		if img_name.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
			img_path = os.path.join(detector.output_image, img_name)
			file = open(img_path, 'rb')
			files = {
					"img": file,
					"json": (None, str(jsonText))
					}
			r = requests.post(ocr_server_url, files=files) # make a form data post request to the ocr service
			print(r.request.headers)
			print(r.content)
			textRespond = (r.content).decode('UTF-8')
			textRespondJson = jsonify(textRespond)
			return textRespondJson
		else:
			return "An Exception accurred", 415
roitextimg_parser = reqparse.RequestParser()
roitextimg_parser.add_argument('img', location='files', type=FileStorage, required=True)
roitextimg_parser.add_argument('json', location='form', required=True, help="The json response of the detecttoarray endpoint")
@ns_conf.route("/roiToTextImg")
@ns_conf.expect(roitextimg_parser)
class ImgRoiToText(Resource):
	def post(self):
		ocr_server_url = "http://172.28.1.6:7000/api/convert"
		args = roitextimg_parser.parse_args()
		uploaded_file = args['img']  # Get the file obj which is the FileStorage instance
		jsonText = args['json'] #get the json from the request
		print(jsonText)
		if uploaded_file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
			file = uploaded_file.read()
			files = {
					"img": file,
					"json": (None,str(jsonText))
					}
			r = requests.post(ocr_server_url, files=files) # make a form data post request to the ocr service
			print(r.request.headers)
			print(r.content)
			textRespond = (r.content).decode('UTF-8')
			textRespondJson = jsonify(textRespond)
			return textRespondJson
		else:
			return "An Exception accurred", 415
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
		self.load_image = '/tensorflow/workspace/gateway/public/tmp/input_img_document.jpg'
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
	def request(self, img_path):
		"""
		Make a prediction request
		POST http://172.28.1.3:8080/v1/models/default:predict
		:return:
		"""
		image = PIL.Image.open(img_path)
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
	def bounding_boxes(self, img_path):
		"""
		Convert bounding boxes to response
		:return: coordinats of the bounding boxes
		"""
		image = Image.open(img_path)
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

@app.after_request
def after_request(response):
	"""
	this function exposes the gatway to other clients then it self.
	this was required because of the CORS policy.
	:return: response with the header Access-Control-Allow-Origin = *
	"""
	response.headers.add('Access-Control-Allow-Origin', '*')
	return response

def requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None):
	"""
	Implementation of retry of http request if failture
	:param retries: the amount of times the request should be repled after it returns connection error
	:param backoff_factor: 
	:param status_forcelist:
	:param session: the request session
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



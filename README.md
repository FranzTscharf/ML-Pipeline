# Clinical Document Classification MLaaS Pipeline

This Project is a part of the paper from Viktor Walter-Tscharf. The ouline of this repo is to make a PoC for clustering and classifying documents.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.
See deployment for notes on how to deploy the project on a live system.

### Prerequisites

This repo is based on docker container and images. Therefore you will need docker

```
sudo apt-get update
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
docker --version
```

### Installing

Clone the repo and navigate to the folder.
```
git clone ...
cd ...
```

Deploy the Docker containers througth Docker compose.

```
cd (to the root folder of the repo - where the docker compose yml is located)
docker-compose up
```
After the completion the services should be up and running.

### Architectur
![Architectur](https://i.imgur.com/I1gVQaSr.png)

## Advanced Single Mode without container
### Setup
```
cd (to the root folder of the repo)

pip install -r requirements.txt
```
### Start api-gateway
we need to start the api-gatway component
```
cd (to the root folder of the repo)
python workspace/gateway/main.py
```
### Start serving
we need to start the serving component
```
cd (to the root folder of the repo)
cd ./workspace/serving/saved_models/
docker run -v `pwd`:/tensorflow/workspace/ -p 8082:8082 -it tensorflow/serving:latest-devel bash
tensorflow_model_server --model_base_path=/models/object-detect --rest_api_port=8082 --port=8081
```
### Start pipeline
we need to start the pipeline component
```
airflow webserver -p 8090 & airflow scheduler
```
### Start ocr
```
cd (to the root folder of the repo)
python ./workspace/ocr/main.py run
```
### Start frontend
```
cd (to the root folder of the repo)
cd ./workspace/frontend/
npm start
```

## Swagger UI API overview
After the installation and local deployment the API should be accessible on localhost:5000.
![alt text](https://i.ibb.co/1M8sVWZ/Screen-Shot-2019-07-04-at-22-02-45.png)

## Pipeline lifecycle management
![alt text](https://i.ibb.co/Tc5ZKMS/Screen-Shot-2019-07-25-at-16-02-20.png)
![alt text](https://i.ibb.co/dPZ833M/Screen-Shot-2019-07-25-at-16-02-32.png)
## Deployment

In the future the services will be deployed to gcp.

## Built With

* [Docker](https://www.docker.com/) - Container
* [Flask](http://flask.pocoo.org/) - Web framework flask
* [Flask-RESTPlus](https://flask-restplus.readthedocs.io/) - API Doc with Swagger UI
* [Tensorflow](https://www.tensorflow.org/) - Deep Learning with tf
* [Tensorflow Serving](https://www.tensorflow.org/tfx/guide/serving) - Productive DL-Modells with tf_serving
* [Tesseract OCR](https://www.tensorflow.org/tfx/guide/serving) - OCR Engine Tesseract

## Dependencies:
	-pytesseract
	-opencv	
	-imutils
	-pillow
	-numpy
	-matplotlib
	-tensorflow-gpu
	-jupyter
	-flask
	-flask_restplus
	-pdf2image
	-scikit-image
	-cython
	-protobuf
	-libsm6
	-libxext6
	-libxrender-dev
	-protobuf-compiler
	-python-pil
	-python-lxml

## Versioning

For the versions available, see the repository. 

## Authors

* **Viktor Walter-Tscharf** - *Initial work*

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.


## Acknowledgments

coming soon
* etc

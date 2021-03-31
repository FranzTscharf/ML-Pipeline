FROM "ubuntu:bionic"
RUN apt-get update && yes | apt-get upgrade
RUN mkdir -p /tensorflow/models
RUN apt-get update && apt-get install -y python3-pip nano curl wget git libsm6 libxext6 libxrender-dev protobuf-compiler python-pil python-lxml
RUN git clone https://github.com/tensorflow/tfx.git /tensorflow/tfx/
WORKDIR /tensorflow/tfx/
RUN pip3 install tfx
ENV AIRFLOW_HOME "/tensorflow/workspace/pipeline/airflow"
RUN pip3 install -U pillow requests numpy matplotlib tensorflow-gpu flask flask_restplus apache-airflow protobuf opencv-python jupyter scikit-image cython
RUN airflow initdb
RUN pip3 install "git+https://github.com/philferriere/cocoapi.git#egg=pycocotools&subdirectory=PythonAPI"
RUN git clone https://github.com/tensorflow/models.git /tensorflow/models
WORKDIR /tensorflow/models/research
RUN protoc object_detection/protos/*.proto --python_out=.
ENV PYTHONPATH "${PYTHONPATH}:/tensorflow/models/research:/tensorflow/models/research/slim"
RUN jupyter notebook --generate-config --allow-root
RUN echo "c.NotebookApp.password = u'sha1:6a3f528eec40:6e896b6e4828f525a6e20e5411cd1c8075d68619'" >> /root/.jupyter/jupyter_notebook_config.py
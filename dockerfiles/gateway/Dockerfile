FROM "ubuntu:bionic"
#VOLUME ./workspace/ /tensorflow/workspace/
RUN apt-get update && yes | apt-get upgrade
RUN mkdir -p /tensorflow/models
RUN apt-get update && apt-get install -y python3-pip nano curl wget git python-pip poppler-utils
RUN pip3 install pillow requests numpy matplotlib tensorflow-gpu jupyter flask flask_restplus pdf2image
RUN pip install --upgrade pip
RUN apt-get install -y libsm6 libxext6 libxrender-dev protobuf-compiler python-pil python-lxml
RUN pip install opencv-python scikit-image cython 
RUN pip install "git+https://github.com/philferriere/cocoapi.git#egg=pycocotools&subdirectory=PythonAPI"
RUN git clone https://github.com/tensorflow/models.git /tensorflow/models
WORKDIR /tensorflow/models/research
RUN protoc object_detection/protos/*.proto --python_out=.
RUN export PYTHONPATH=$PYTHONPATH:/tensorflow/models/research:/tensorflow/models/research/slim
ENV PYTHONPATH "${PYTHONPATH}:/tensorflow/models/research:/tensorflow/models/research/slim"
RUN jupyter notebook --generate-config --allow-root
RUN echo "c.NotebookApp.password = u'sha1:6a3f528eec40:6e896b6e4828f525a6e20e5411cd1c8075d68619'" >> /root/.jupyter/jupyter_notebook_config.py
#CMD ["jupyter", "notebook", "--allow-root", "--notebook-dir=/tensorflow/models/research/object_detection", "--ip=0.0.0.0", "--port=8888", "--no-browser"]
RUN pip3 install Werkzeug==0.16.1 --force-reinstall


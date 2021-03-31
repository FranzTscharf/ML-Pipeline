FROM "ubuntu:bionic"
RUN apt-get update && yes | apt-get upgrade
RUN apt update && apt install -y libsm6 libxext6 libxrender-dev
RUN apt-get update && apt-get install python3-pip nano curl wget tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng -y
RUN pip3 install pytesseract
RUN pip3 install flask
RUN pip3 install opencv-python
RUN pip3 install numpy
RUN pip3 install imutils
RUN pip3 install scikit-image
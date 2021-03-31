import os
import cv2
import pytesseract
import json
import sys
from PIL import Image
from PIL import ImageOps
from flask import Flask, request, render_template, url_for, redirect, jsonify, Response
from pyimagesearch.transform import four_point_transform
from skimage.filters import threshold_local
import numpy as np
import argparse
import cv2
import imutils
import datetime

############## SETTINGS ##################
template_path = '/tensorflow/workspace/ocr/public/templates/' # path to the html template folder.
static_folder = '/tensorflow/workspace/ocr/public/' # path to the public folder of the ocr server
output_path = '/tensorflow/workspace/ocr/public/tmp/'  # the path where the uploaded images should be saved too.
##########################################

app = Flask(__name__, template_folder=template_path,static_folder=static_folder)

@app.route("/")
def fileFrontPage():
    """
    this returns the index page
    :return: front page
    """
    return render_template('fileform.html') # return the html template of the upload form.
    
@app.route("/receipts")
def receiptsFrontPage():
    """
    this returns the index page of the receipts
    :return: front page of receipts
    """
    return render_template('receipts.html') # return the html template of the upload form of receipts.

@app.route("/handleReceipts", methods=['POST'])
def handleReceiptsUpload():
    """
    this function handels if the form got submited.
    :return:
    """
    if 'photo' in request.files:
        photo = request.files['photo'] # get the file
        imgPath = os.path.join(output_path, photo.filename) # construct the img save path
        if photo.filename != '': #check if not null           
            photo.save(imgPath) # save the uploaded image
            pathOfConvertedImg, tmpFileName = cutReceiptOutOfImg(imgPath)
    #return redirect(url_for('fileFrontPage'))
    print(pathOfConvertedImg)
    text = decodeText(pathOfConvertedImg) # function call for detect txt in img.
    jsonTxt = r"""{'filename':'"""+ str(tmpFileName) +"""', 'filepath': '"""+str(pathOfConvertedImg)+"""', 'url':'"""+request.remote_addr+url_for('static', filename='tmp/'+str(photo.filename))+"""','text': '"""+str(text)+"""'}"""
    return render_template('resultReceipts.html', imgpath = url_for('static', filename='tmp/'+str(tmpFileName)), json=jsonTxt)


@app.route("/handleUpload", methods=['POST'])
def handleFileUpload():
    """
    this function handels if the form got submited.
    :return:
    """
    if 'photo' in request.files:
        photo = request.files['photo'] # get the file
        imgPath = os.path.join(output_path, photo.filename) # construct the img save path
        if photo.filename != '': #check if not null           
            photo.save(imgPath) # save the uploaded image
    #return redirect(url_for('fileFrontPage'))
    text = decodeText(imgPath) # function call for detect txt in img.
    jsonTxt = r"""{'filename':'"""+ str(photo.filename) +"""', 'filepath': '"""+str(imgPath)+"""', 'url':'"""+request.remote_addr+url_for('static', filename='tmp/'+str(photo.filename))+"""','text': '"""+str(text)+"""'}"""
    return render_template('result.html', imgpath = url_for('static', filename='tmp/'+str(photo.filename)), json=jsonTxt)

@app.route("/api", methods=['POST'])
def api():
    """
    this function is responsible for using the api.
    :return:
    """
    if request.method == 'GET': #check if not the wrong request!
        return 'wrong request, try POST'
    else:
        if 'photo' in request.files:
            photo = request.files['photo'] # get the file
            imgPath = os.path.join(output_path, photo.filename) # construct the img save path
            if photo.filename != '': #check if not null           
                photo.save(imgPath) # save the uploaded image
        #return redirect(url_for('fileFrontPage'))
        text = decodeText(imgPath) # function call for detect txt in img.
        jsonTxt = r"""{'filename':'"""+ str(photo.filename) +"""', 'filepath': '"""+str(imgPath)+"""', 'url':'"""+request.remote_addr+url_for('static', filename='tmp/'+str(photo.filename))+"""','text': '"""+str(text)+"""'}"""
        return jsonify(jsonTxt)
@app.route("/api", methods=['GET'])
def version():
    """
    this function calls tesseract and identifies the version.
    :return: tesseract version
    """
    return 'Tesseract OCR '+str(getversion())

@app.route("/api/convert", methods=['POST'])
def convert():
    """
    this function takes a img file in the form key 'photo'.
    also is taking the output of the rbci detecttoarray entpoint in the body.
    :return:
    """
    if request.form.get('json') != '' and 'img' in request.files: #check if the body arguments img and json are in the body of the request
        img = request.files['img'] # get the file
        jsonText = request.form.get('json')
        imgPath = os.path.join(output_path, img.filename) # construct the img save path
        if img.filename != '': #check if not null
            img.save(imgPath) # save the uploaded image
        else:
            return 'filename is not valide'
        parsed = json.loads(jsonText)
        classKeyTextJson = {} # init json
        for index, each in enumerate(parsed):
            #                                      1616, 525,  2450, 1019
            #order: 0,1,2,3,4,5 => classe, score, xmin, ymin, xmax, ymax.
            #    (left, right, top, bottom) = (xmin * im_width, xmax * im_width, ymin * im_height, ymax * im_height)
            classKeyName = each[0] #this could be customer,identification,type,header or content.
            xmin = each[2]
            ymin = each[3]
            xmax = each[4]
            ymax = each[5]
            print(classKeyName,xmin,ymin,xmax,ymax)
            try:
                classKeyText = decodeTextInRegion(imgPath,classKeyName,xmin,ymin,xmax,ymax)
                classKeyTextJson[str(classKeyName)] = classKeyText
                print(each)
            except:
                print('An exception occurred')   #if exection happens
        return Response(response=str(classKeyTextJson),status=200,mimetype="text/json")
    else:
        return 'body is empty'
def cutReceiptOutOfImg(imgPath):
    """
    this function is a helper to cut the Receipt out of the image and improve the detection. This
    includes the detection of the edges of the Receipt.
    :return:
    """
    # load the image and compute the ratio of the old height
    # to the new height, clone it, and resize it
    image = cv2.imread(imgPath)
    ratio = image.shape[0] / 1000.0
    orig = image.copy()
    image = imutils.resize(image, height = 1000)
    # convert the image to grayscale, blur it, and find edges
    # in the image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 75, 200)
    cv2.imwrite(output_path + "image.jpg", image)
    cv2.imwrite(output_path + "edged.jpg", edged)
    try:
        # find the contours in the edged image, keeping only the
        # largest ones, and initialize the screen contour
        cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]
        # loop over the contours
        print(cnts)
        for c in cnts:
            # approximate the contour
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.03 * peri, True)
            # if our approximated contour has four points, then we
            # can assume that we have found our screen
            if len(approx) == 4:
                screenCnt = approx
                break
        # show the contour (outline) of the piece of paper
        print("STEP 2: Find contours of paper")
        cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
        cv2.imwrite(output_path + "outline.jpg", image)
        # apply the four point transform to obtain a top-down
        # view of the original image
        warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
        # convert the warped image to grayscale, then threshold it
        # to give it that 'black and white' paper effect
        warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        T = threshold_local(warped, 11, offset = 10, method = "gaussian")
        warped = (warped > T).astype("uint8") * 255
        # show the original and scanned images
        print("STEP 3: Apply perspective transform")
        tmpFileName = "img_scan_"+datetime.datetime.now().strftime("%Y-%m-%d%_H-%M-%s")+".jpg"
        pathOfConvertedImg = output_path + tmpFileName
        cv2.imwrite(pathOfConvertedImg, warped)
        return pathOfConvertedImg, tmpFileName
    except Exception as e:
        print ("could not find the contours of the image", e)
        return "", ""

def getversion():
    """
    this function is a helper to get the current version of tesseract-ocr.
    :return:
    """
    version = pytesseract.get_tesseract_version()
    return version

def convertText(text):
    """
    this function is deleting the utf-8 chapters of single quotations and double once.
    this chapters are responsible for causing problems for further processing in js with json.
    :param text: the resonse from tesseract.
    :return: text without quotations.
    """
    #text = text.encode('utf8')
    text = str(text).replace("'","").replace('"',"")
    text = text.replace('"','\\"').replace("‘", '').replace("’", '')
    text = text.replace("'", '').replace("'", '').replace(u"\u2018", "")
    text = text.replace(u"\u2019", "").replace("'","").replace(u'\u0027',"")
    return text
def decodeText(imgPath):
    """
    this function calls tesseract and executes a simple ocr detection.
    :param imgPath: the image path of the uploaded img.
    :return: the text response from tesseract.
    """
    #config = ('-l deu+eng --oem 1 --psm 3 --dpi 300')
    config = ('-l deu+eng --oem 1 --psm 3 --dpi 300') # Settings for the tesseract engine, languages, ocrenginemode, pagesegmode and dots per inch.
    im = cv2.imread(imgPath, cv2.IMREAD_COLOR) # convert img to array
    text = pytesseract.image_to_string(im, config=config) # call tesseract throught pytesseract api with the config arguments
    return convertText(text)
def decodeTextInRegion(imgPath,classKeyName,xmin,ymin,xmax,ymax):
    """
    This function uses tesseract to decode the different roi images of the specific content.
    :param imgPath: the path of the uploaded image.
    :param classKeyName: the name of the detected class from tensorflow.
    :param xmin: the xmin value e.g. position returned from tensorflow.
    :param ymin: the ymin value e.g. position returned from tensorflow.
    :param xmax: the xmax value e.g. position returned from tensorflow.
    :param ymax: the ymax value e.g. position returned from tensorflow.
    :return: is returning the text in the roi of the coordinates.
    """
    img = Image.open(imgPath)
    width, height = img.size
    #fuction #left, up, right, bottom
    border = (xmin, ymin, width-xmax, height-ymax)
    cropped_im = ImageOps.crop(img, border).copy()
    cropped_im.save(output_path+'outtest_'+str(classKeyName)+'.jpg')
    classKeyText = pytesseract.image_to_string(cropped_im)
    return convertText(classKeyText)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000)   
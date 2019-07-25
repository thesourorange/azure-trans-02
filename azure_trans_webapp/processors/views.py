from flask import Flask, Blueprint, render_template, request, send_file
import numpy as np
import binascii
import ctypes
import codecs
import struct
import sys
import re
import argparse
import csv
import re
import json
import threading
import datetime
from os import environ
import os
import tempfile
import string
import multiprocessing as mp
import gc
import numpy as np
import tensorflow as tf
import requests
import cv2 as cv
import six.moves.urllib as urllib
import tarfile
import base64
import io
import threading

from struct import unpack, pack

images = {}
timer = None

views = Blueprint('views', __name__, template_folder='templates')

# What model to download.
MODEL_NAME = 'ssd_mobilenet_v1_coco_2018_01_28'
MODEL_FILE = MODEL_NAME + '.tar.gz'
DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'

def get_images():
   print(str(datetime.datetime.now()) + " : " + "Obtaining images")
  
   configuration = getConfiguration()
   
   f = open(configuration['debug_file'], 'a')
    
   try:
      s = requests.Session()
      headers = {'Accept': 'application/json',
           'Authorization' : 'apikey oxsSR3dlvdnVK2XTLEudKmIjRuODY5TsSKSD'}

      req = s.get('https://api.transport.nsw.gov.au/v1/live/cameras', headers=headers)
  
      result = req.json()
      counter = 0
      print(str(datetime.datetime.now()) + " : Getting Images")

      for feature in result['features']:
         id = feature['id']
         properties = feature['properties']

         obtaining_image = True

         while obtaining_image: 
            print(str(datetime.datetime.now()) + " : [" + str(counter) + "] : Retrieving: " + id + " - " + properties['href'])
      
            try:
               resp = urllib.request.urlopen(properties['href'])
               image = np.asarray(bytearray(resp.read()), dtype="uint8")
               image = cv.imdecode(image, cv.IMREAD_COLOR)

               images[id] = image
               obtaining_image = False
               counter += 1

            except Exception as e:
               print(e)

   except Exception as e:

      print(str(datetime.datetime.now()) + " : " + str(e))
  
      log(f, str(e))

   print(str(datetime.datetime.now()) + " : Completed ")
   f.close()

def log(f, message):
   f.write(str(datetime.datetime.now()))
   f.write(' : ')
   f.write(message)
   f.write('\n')
   f.flush()

   print(str(datetime.datetime.now()) + ' : ' + message)

def getConfiguration():    
   transport_key = None
   debug_file = None
   trans_url = None

   try:
      import azure_trans_webapp.configuration as config

      transport_key = config.TRANSPORT_KEY
      debug_file = config.DEBUG_FILE
      trans_url = config.TRANS_URL
    
   except ImportError:
      pass

   transport_key = environ.get('TRANSPORT_KEY', transport_key)
   debug_file = environ.get('DEBUG_FILE', debug_file)
   trans_url = environ.get('TRANS_URL', trans_url)

   return {
      "transport_key": transport_key,
      "debug_file": debug_file,
      
   }   

def unsharp_mask(image, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
    """Return a sharpened version of the image, using an unsharp mask."""
    blurred = cv.GaussianBlur(image, kernel_size, sigma)
    sharpened = float(amount + 1) * image - float(amount) * blurred
    sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
    sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
    sharpened = sharpened.round().astype(np.uint8)
    if threshold > 0:
        low_contrast_mask = np.absolute(image - blurred) < threshold
        np.copyto(sharpened, image, where=low_contrast_mask)
    return sharpened

def process_image(f, id):
   detection_graph = tf.Graph()
   with detection_graph.as_default():
      graph_def = tf.GraphDef()
   with tf.gfile.GFile(os.getcwd() + "/" + MODEL_NAME + '/frozen_inference_graph.pb', 'rb') as fid:
      serialized_graph = fid.read()
      graph_def.ParseFromString(serialized_graph)
   with tf.Session() as sess:
      tf.import_graph_def(graph_def, name='')
      img = np.copy(images[id])
      rows = img.shape[0]
      cols = img.shape[1]
      
      scale = 10
    
      width = int(img.shape[1] * scale) 
      height = int(img.shape[0] * scale) 
      dim = (width, height) 
      inp = cv.resize(img, dim, interpolation = cv.INTER_AREA) 
      inp = unsharp_mask(inp)

      inp = inp[:, :, [2, 1, 0]]
      out = sess.run([sess.graph.get_tensor_by_name('num_detections:0'),
                    sess.graph.get_tensor_by_name('detection_scores:0'),
                    sess.graph.get_tensor_by_name('detection_boxes:0'),
                    sess.graph.get_tensor_by_name('detection_classes:0')],
                   feed_dict={'image_tensor:0': inp.reshape(1, inp.shape[0], inp.shape[1], 3)})
      num_detections = int(out[0][0])
      log(f, "Num of detections: " + id + " - " + str(num_detections) + "  - [ " + str(width) + ":" + str(height) + "]")
     
      for i in range(num_detections):
         classId = int(out[3][0][i])
         score = float(out[1][0][i])
         bbox = [float(v) for v in out[2][0][i]]
         if score > 0.1:
            x = bbox[1] * cols
            y = bbox[0] * rows
            right = bbox[3] * cols
            bottom = bbox[2] * rows
            cv.rectangle(img, (int(x), int(y)), (int(right), int(bottom)), (125, 255, 51), thickness=2)

   is_success, buffer = cv.imencode('.png', img)
   bytes = io.BytesIO(buffer)
   bytes.seek(0)
   return base64.b64encode(bytes.read())   

@views.route("/")
def home():
   return render_template("main.html")

@views.route("/get", methods=["GET"])
def get():
   id = request.args.get('id')
       
   image = images[id]
   rows = image.shape[0]
   cols = image.shape[1]

   is_success, buffer = cv.imencode('.png', image)
   bytes = io.BytesIO(buffer)
   bytes.seek(0)

   return send_file(bytes, mimetype='image/png')


@views.route("/identify", methods=["GET"])
def identify():
   configuration = getConfiguration()
   f = open(configuration['debug_file'], 'a')
   id = request.args.get('id')
   log(f, "Processing - id:'" + id + "'")

   return process_image(f, id)
 
@views.route("/retrieve", methods=["GET"])
def list():
   configuration = getConfiguration()
   
   f = open(configuration['debug_file'], 'a')
    
   try:
      s = requests.Session()
      headers = {'Accept': 'application/json',
           'Authorization' : 'apikey oxsSR3dlvdnVK2XTLEudKmIjRuODY5TsSKSD'}

      req = s.get('https://api.transport.nsw.gov.au/v1/live/cameras', headers=headers)
  
      return json.dumps(req.json(), sort_keys=True)

   except Exception as e:
      log(f, str(e))

      f.close()
      return ""

@views.route("/refresh", methods=["GET"])
def refresh():
   get_images()

   keys = []

   for image in images:
      keys.append(image)

   req = {

      'images' : keys

   }

   return json.dumps(req, sort_keys=True)

def startup():
   print(str(datetime.datetime.now()) + " : " + "Obtaining model")

   opener = urllib.request.URLopener()
   opener.retrieve(DOWNLOAD_BASE + MODEL_FILE, MODEL_FILE)
   tar_file = tarfile.open(MODEL_FILE)
   for file in tar_file.getmembers():
      file_name = os.path.basename(file.name)
      if 'frozen_inference_graph.pb' in file_name:
         tar_file.extract(file, os.getcwd())    
         print(str(datetime.datetime.now()) + " : " + "Obtained tar extract - '" + os.getcwd() + os.pathsep + "frozen_inference_graph.pb")

   print(str(datetime.datetime.now()) + " : " + "Obtained model - '" + os.getcwd() + "'")

   get_images()

threading.Timer(1.0, startup).start()


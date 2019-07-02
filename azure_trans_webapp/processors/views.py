from flask import Flask, Blueprint, render_template, request
import binascii
import ctypes
import codecs
import struct
import sys
import re
import argparse
import csv
import io
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
from matplotlib import pyplot as plt

import six.moves.urllib as urllib
import tarfile

from struct import unpack, pack

views = Blueprint('views', __name__, template_folder='templates')

# What model to download.
MODEL_NAME = 'ssd_mobilenet_v1_coco_2018_01_28'
MODEL_FILE = MODEL_NAME + '.tar.gz'
DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'

def log(f, message):
   f.write(str(datetime.datetime.now()))
   f.write(' : ')
   f.write(message)
   f.write('\n')
   f.flush()

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

def url_to_image(url):
    # download the image, convert it to a NumPy array, and then read
    # it into OpenCV format
    resp = urllib.request.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
 
    # return the image
    return image

def process_image(url):
   detection_graph = tf.Graph()
   with detection_graph.as_default():
      graph_def = tf.GraphDef()
   with tf.gfile.GFile(os.getcwd() + MODEL_NAME + '/frozen_inference_graph.pb', 'rb') as fid:
      serialized_graph = fid.read()
      graph_def.ParseFromString(serialized_graph)
   with tf.Session() as sess:
      tf.import_graph_def(graph_def, name='')
      img = url_to_image("url")


@views.route("/")
def home():
   return render_template("main.html")

@views.route("/identify", methods=["GET"])
def identify():
   f = open(configuration['debug_file'], 'a')
   url = request.args.get('url')
   log(f, "Processing - url:'" + url + "'")
   return ""

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

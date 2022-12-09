import os
import sys
#import math
import numpy as np
import skimage.io
#import matplotlib
#import matplotlib.pyplot as plt
import tensorflow as tf
from keras.backend.tensorflow_backend import set_session

#model will block on port and send on port+1

def modelProcess(port,gpuID,gpuMemoryFraction,numberOfGPUs,numberOfProcessesPerGPU):
    ROOT_DIR = os.path.abspath("./Mask_RCNN")

    sys.path.append(ROOT_DIR)
    #from mrcnn import utils
    import mrcnn.model as modellib
    #from mrcnn import visualize
    from mrcnn import config
    MODEL_DIR = os.path.join(ROOT_DIR,"trainedWeights")

    MODEL_PATH = os.path.join(MODEL_DIR,"weights1.h5")

    if not os.path.exists(MODEL_PATH):
        print("No weights found in MODEL_PATH add a weights1.h5 file")
        exit()
    from multiprocessing.connection import Listener
    from multiprocessing.connection import Client
    #import time
     


    addrSendsocket = ('localhost', port+1)
    addrBlocksocket = ('localhost', port)

    blockSocket = Listener(addrBlocksocket, authkey='oleole'.encode())
    class InferenceConfig(config.Config):
        NAME = "inferenceConfig"
        GPU_COUNT = 1
        IMAGES_PER_GPU = 1
        NUM_CLASSES = 1 + 1
        BATCH_SIZE = 1

    config=InferenceConfig()
    config.display()
    ######################### Session Configuration #####################
    sessconfig=tf.ConfigProto()
    sessconfig.gpu_options.visible_device_list=str(gpuID)
    sessconfig.gpu_options.per_process_gpu_memory_fraction=gpuMemoryFraction #0.15
    #sessconfig.gpu_options.allow_growth=True
    set_session(tf.Session(config=sessconfig))
    #####################################################################
    model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)
    model.load_weights(MODEL_PATH, by_name=True)
    #########run a sample image inference so that libcudnn is opened#####
    _img=skimage.io.imread("./Mask_RCNN/images/1.jpg")
    _=model.detect([_img],verbose=0)
    print("MODEL CREATED",port)
    class_names = ['BG', 'car']

    #continuously run detection
    while True:
        conn = blockSocket.accept()
        #time.sleep(0.01)
        sendSocket = Client(addrSendsocket, authkey='oleole'.encode())
        images=conn.recv()
        print("images recv")
        detections=[]
        for img in images:
            det=model.detect([img],verbose=0)
            print("ran detection",port)
            detections.append(det[0])
        sendSocket.send(detections)
        conn.close()
        sendSocket.close()
        


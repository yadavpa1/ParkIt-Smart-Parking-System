#from sendImagesToModel import send_images_to_model
import skimage.io
import os
import sys
#import math
#import numpy as np
#import matplotlib
#import matplotlib.pyplot as plt
import random
from threading import Thread
from time import sleep
import time
from multiprocessing.connection import Listener
from multiprocessing.connection import Client
from multiprocessing import Process
from multiprocessing import Array
ROOT_DIR = os.path.abspath("./Mask_RCNN")

sys.path.append(ROOT_DIR)
#from mrcnn import utils
#import mrcnn.model as modellib
from mrcnn import visualize
#from mrcnn import config
#MODEL_DIR = os.path.join(ROOT_DIR,"trainedWeights")
class_names = ['BG', 'car']


def send_images_to_concurrent_models(images,numberOfModels,startPort):
    ports=[]
    tmp=startPort
    for i in range(numberOfModels):
        ports.append(tmp)
        tmp=tmp+2
    imagesPerModel=int(len(images)/numberOfModels)
    if imagesPerModel == 0 or len(images)==numberOfModels:
        ports = random.sample(ports, len(images))
        threads = [None] * len(images)
        result = [None] * len(images)
        #result = Array('i',len(images))
        for i in range(len(images)):
            threads[i] = Thread(target=_send_images_to_model, args=(images[:1],ports[i],result,i))
            #threads[i] = Process(target=_send_images_to_model, args=(images[:1],ports[i],result,i))
            del images[:1]
            threads[i].start()
        for i in range(len(threads)):
            threads[i].join()
        detections=[]
        for res in result:
            for det in res:
                detections.append(det)

    else:
        extra = len(images)%numberOfModels
        threads = [None] * numberOfModels
        result = [None] * numberOfModels
        #result = Array('i',numberOfModels)
        sliceIndex = imagesPerModel
        for i in range(numberOfModels):
            threads[i] = Thread(target=_send_images_to_model, args=(images[:sliceIndex],ports[i],result,i))
            #threads[i] = Process(target=_send_images_to_model, args=(images[:sliceIndex],ports[i],result,i))
            del images[:sliceIndex]
            threads[i].start()
            if i == numberOfModels-(extra+1):
                sliceIndex+=1
        for i in range(len(threads)):
            threads[i].join()
        detections=[]
        for res in result:
            for det in res:
                detections.append(det)
        

    return detections

def _send_images_to_model(images,port,result,index):
    addrSendSocket = ('localhost',port)
    addrBlockSocket = ('localhost', port+1)
    while True:
        try:
            blockSocket = Listener(addrBlockSocket, authkey='oleole'.encode())
            print('opened listener on',port+1)
            break
        except os.error as e:
            sleep(0.01)
            continue
    sleep(0.001)
    sendSocket = Client(addrSendSocket, authkey='oleole'.encode())
    conn = blockSocket.accept()
    sendSocket.send(images)
    detections = conn.recv()
    conn.close()
    sendSocket.close()
    blockSocket.close()
    result[index]=detections

######################### Parsing arguments #########################
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='create the model object and listen for images on the specified ports')
    parser.add_argument('--port',required=True,help='port on which the program has to send for inference requests')
    
    args = parser.parse_args()


#####################################################################

image1 = skimage.io.imread("/home/poojay/environments/DL/Mask_RCNN/images/4.jpg")
image2 = skimage.io.imread("/home/poojay/environments/DL/Mask_RCNN/images/4.jpg")
image3 = skimage.io.imread("/home/poojay/environments/DL/Mask_RCNN/images/4.jpg")
image4 = skimage.io.imread("/home/poojay/environments/DL/Mask_RCNN/images/4.jpg")
#image5 = skimage.io.imread("/home/poojay/environments/DL/Mask_RCNN/images/test5.jpg")
#image6 = skimage.io.imread("/home/poojay/environments/DL/Mask_RCNN/images/test6.jpg")
#image7 = skimage.io.imread("/home/poojay/environments/DL/Mask_RCNN/images/test7.jpg")
#image8 = skimage.io.imread("/home/poojay/environments/DL/Mask_RCNN/images/test8.jpg")
#image9 = skimage.io.imread("/home/poojay/environments/DL/Mask_RCNN/images/test9.jpg")
#image10 = skimage.io.imread("/home/poojay/environments/DL/Mask_RCNN/images/test10.jpg")

print("KAKAKAKAKAKAKAKAKAKKAKAA")
start_time = time.time()
results=send_images_to_concurrent_models([image1,image2,image3,image4],4,int(args.port))
print("--- %s seconds ---"%(time.time()-start_time))
print("mamamamamamamamamamamamam")
r=results[0]
print(image1.shape)
#print(r['masks'].shape)

visualize.display_instances(image1, r['rois'], r['masks'], r['class_ids'],
                            class_names, r['scores'],show_bbox=True)



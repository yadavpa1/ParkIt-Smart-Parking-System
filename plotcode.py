from roipoly import RoiPoly #pip install git+https://github.com/jdoepfert/roipoly.py
import matplotlib.pyplot as plt
import cv2
import os,sys
import time
import pickle
from multiprocessing.connection import Client
from multiprocessing.connection import Listener
import requests
import matplotlib.pyplot as plt
def first_time_install(numberOfCameras):
    allrois=[]   #gives the rois for every camera
    for i in range(numberOfCameras):
        cap=cv2.VideoCapture(i)
        cap.set(3,1280)
        cap.set(4,720)
        #read call multiple times to get the camera ready else img comes black
        _,img=cap.read()
        _,img=cap.read()
        _,img=cap.read()
        _,img=cap.read()
        _,img=cap.read()
        _,img=cap.read()
        img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        rois=[]
        breakFlag=False
        while True:
            fig=plt.figure(figsize=(12,10))
            if len(rois) > 0:
                for j in range(len(rois)):
                    try:
                        rois[j].display_roi()
                    except IndexError:
                        breakFlag=True
                        break
            if breakFlag == True:
                break
            plt.imshow(img)
            rois.append(RoiPoly(color='r',fig=fig))
            plt.show(block=True)
        del rois[len(rois)-1]
        allrois.append(rois)
        plt.close('all')
        cap.release()
    
    # store allrois object on disk
    pickle_out = open("allrois.pickle","wb")
    pickle.dump(allrois, pickle_out)
    pickle_out.close()
    
    """ -----CHAITANYA insert below the #comment below this docstring-----
    static ip ,longitude vagre are the inputs to this funtion which are to be sent to the main server.
    The allrois.pickle file will contain a list of lists of RoiPoly objects. One list for each camera.
    The python object from allrois.pickle can be obtained on the server by pickle.load() method
    """
    #send allroi object to main server and also send coordinates of parklot and static ip
    url="http://ourserver.com/firstTimeInstall/"
    pickle_in = open("allrois.pickle","rb")
    

    pickle_in.close()
    return allrois



##the script needs two coomand line arguments (--install tells whether this is first time installation) and (--numberOfCameras which is self explanatory)
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--install',required=True,help='True when the local computer is newly installed or arrangement of cameras is changed')
    parser.add_argument('--numberOfCameras',required=True,help='the number of cameras connected to the local computer')
    args=parser.parse_args()

######################################################################################
if(args.install=='True'):
    install=True
else:
    install=False
numberOfCameras=int(args.numberOfCameras)

######################################################################################
if install==True:
    _,data=first_time_install(numberOfCameras)
#####################################################################################

#testing code
#pickle_in = open("allrois.pickle","rb")
#allrois = pickle.load(pickle_in)
#allrois = pickle.load(data['allrois'])
#print(allrois)
#####################################################################################

# below code is the main code which blocks on port number 33333 for requests for images from parking lot
addrBlocksocket = ('0.0.0.0',33333)
addrSendsocket = ('192.168.2.2',44444)
blockSocket = Listener(addrBlocksocket, authkey='leoleo'.encode())

cap=[]  #cap stores the VideoCapture objects for each camera
for i in range(numberOfCameras):
    cap.append(cv2.VideoCapture(i))
    cap[i].read()   #cap.read() is called to get the cameras ready

print("while started")
while True:
    conn=blockSocket.accept()
    sendSocket = Client(addrSendsocket, authkey='leoleo'.encode())
    metadata=conn.recv()
    print("conn.recv() over")
    images=[]
    for i in range(numberOfCameras):
        _,frame=cap[i].read()
        images.append(frame)
    #plt.imshow(images[2])
    #plt.show()
    sendSocket.send(images)
    print("sent images")
    sendSocket.close()
    conn.close()







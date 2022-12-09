
from modelProcess import modelProcess
from multiprocessing import Process
#from multiprocessing.shared_memory import SharedMemory
"""
download posix_ipc from https://pypi.org/project/posix_ipc/

also do
~/pyEnvs/dlenv/bin/python3.6 setup.py install
to get posix_ipc in virtualenv
"""
import numpy as np
if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--numberOfGPUs',required=True)
    parser.add_argument('--numberOfProcessesPerGPU',required=True)
    parser.add_argument('--GPUMemoryFraction',required=True)
    parser.add_argument('--startingPortNumber',required=True)
    args=parser.parse_args()


numberOfGPUs=int(args.numberOfGPUs)
numberOfProcessesPerGPU=int(args.numberOfProcessesPerGPU)
GPUMemoryFraction=float(args.GPUMemoryFraction)
startingPortNumber=int(args.startingPortNumber)

"""
from posix_ipc import SharedMemory
import posix_ipc
shm= SharedMemory(name='B',size = numberOfGPUs*numberOfProcessesPerGPU,flags=posix_ipc.O_CREX)
print(type(shm))
print(shm[0])
## Create a shared memory which contains locks for each model process
#flags=np.ones(numberOfProcessesPerGPU*numberOfGPUs,dtype=np.int8)

#shm = SharedMemory(name='ModelAccessFlagsSHM',create=True, size=flags.nbytes)

#####################################################################
"""
p=[]

tport=startingPortNumber
for i in range(numberOfGPUs):
    for j in range(numberOfProcessesPerGPU):
        p.append(Process(target=modelProcess, args=(tport,i,GPUMemoryFraction,numberOfGPUs,numberOfProcessesPerGPU)))
        tport=tport+2
        p[len(p)-1].start()

for i in range(len(p)):
    p[i].join()






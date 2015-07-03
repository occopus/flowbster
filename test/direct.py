from ndimCollector import ndimCollector
import pprint
import time

job = ndimCollector(1)
job.addDim("G1",4,1,False,[2,2])
job.addItem("G1",0,[0,0])

job.dump()

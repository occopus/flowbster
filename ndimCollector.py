import yaml
import os

class ndimCollector:

    def __init__ (self,maxdim):
        self.s={}
        self.s['maxdim'] = maxdim
        self.s['numOfDims'] = 0
        self.s['lengthOfDims'] = [0] * self.s['maxdim']
        self.s['maxsize'] = 0
        self.s['normDimInd'] = [-1] * self.s['maxdim']
        self.s['nameOfDims'] = [""] * self.s['maxdim']
        self.s['listOfLists'] = [0]
        self.s['hitList'] = []
        return

    def getNormIndexList(self,dimList):
        normIndexList = [-1] * self.s['maxdim']
        for index,item in enumerate(self.s['normDimInd']):
            normIndexList[index] = dimList[item]
        return normIndexList

    def addItemCheck(self,value,dimList):
        if value == self.s['maxdim']:
            normIndexList = self.getNormIndexList(dimList)
            #print "HIT at position: ",dimList,"Normalised: ",normIndexList,"Base: ",self.s['normDimInd']
            self.s['hitList'].append(normIndexList)
        return

    def addItemScanner(self,dimList,dimIndex,itemIndex,elist,deepness):
        #print "DL:",dimList,"DI:",dimIndex," II:",itemIndex," DEEP:",deepness," EL:",elist
        if dimIndex > 0:
            for index, item in enumerate(elist):
                dimList[self.s['numOfDims']-deepness]=index
                self.addItemScanner(dimList,dimIndex-1,itemIndex,elist[index],deepness-1)
        if dimIndex == 0:
            if deepness == 1:
                elist[itemIndex]+=1
                dimList[self.s['numOfDims']-deepness]=itemIndex
                self.addItemCheck(elist[itemIndex],dimList)
            else:
                dimList[self.s['numOfDims']-deepness]=itemIndex
                self.addItemScanner(dimList,dimIndex-1,itemIndex,elist[itemIndex],deepness-1)
        if dimIndex < 0:
            if deepness == 1:
                for index, item in enumerate(elist):
                    elist[index] +=1
                    dimList[self.s['numOfDims']-deepness]=index
                    self.addItemCheck(elist[index],dimList)
            else:
                for index, item in enumerate(elist):
                    dimList[self.s['numOfDims']-deepness]=index
                    self.addItemScanner(dimList,dimIndex-1,itemIndex,elist[index],deepness-1)
        return

    def addItem(self,name,itemIndex):
        dimIndex = self.s['nameOfDims'].index(name)
        #print "=== add item ",name,"(",dimIndex,") at position ",itemIndex,"."
        if dimIndex >= self.s['numOfDims']:
            print "ERROR: given dim (",dimIndex,") is greater than actual(",self.s['numOfDims'],") !"
        else:
            dimList = [-1] * self.s['numOfDims']
            self.addItemScanner(dimList,dimIndex,itemIndex,self.s['listOfLists'],self.s['numOfDims'])

    def expandListByOneDim(self,elist,deepness,length):
        if deepness == 2:
            for index, item in enumerate(elist):
                value = elist[index] 
                elist[index] = [value] * length
        else:
            for index, item in enumerate(elist):
                self.expandListByOneDim(elist[index],deepness-1,length)
        return

    def checkDimExists(self,name):
        if name in self.s['nameOfDims']:
            return True
        else:
            return False

    def addDim(self,name,length,normDimInd):
        #print "=== add dim \"",name,"\" width length of ",length,"."
        if self.s['numOfDims'] < self.s['maxdim'] :
            self.s['numOfDims']+=1
            self.s['nameOfDims'][self.s['numOfDims']-1]=name
            self.s['normDimInd'][self.s['numOfDims']-1]=normDimInd
            self.s['lengthOfDims'][self.s['numOfDims']-1]=length
            if self.s['numOfDims'] == 1:
                self.s['listOfLists'] = [0] * length
                self.s['maxsize'] = length
            else:
                self.expandListByOneDim(self.s['listOfLists'],self.s['numOfDims'],length)
                self.s['maxsize'] = self.s['maxsize'] * length

    def getNumOfDim(self):
        return self.s['numOfDims']

    def getDimNames(self):
        return self.s['nameOfDims']

    def getDimLengths(self):
        return self.s['lengthOfDims']

    def getMaxSize(self):
        return self.s['maxsize']

    def getHitList(self):
        return self.s['hitList']

    def getHitListHead(self):
        if self.s['hitList']:
            return self.s['hitList'][0]
        else:
            return []

    def removeHitListHead(self):
        if self.s['hitList']:
            self.s['hitList']=self.s['hitList'][1:]
        return

    def serialise(self,path):
        with open(path, 'w') as f: 
            f.write(yaml.dump(self.s,default_flow_style=False))
        return

    def reset(self):
        self.s['numOfDims'] = 0
        self.s['lengthOfDims'] = [0] * self.s['maxdim']
        self.s['maxsize'] = 0
        self.s['normDimInd'] = [-1] * self.s['maxdim']
        self.s['nameOfDims'] = [""] * self.s['maxdim']
        self.s['listOfLists'] = [0]
        self.s['hitList'] = []
        return

    def deserialise(self,path):
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.s=yaml.load(f)
        else:
            self.reset()
        return

    def dump(self):
        print "MaxDim:",self.s['maxdim']
        print "NumDim:",self.s['numOfDims']
        print "DimNames:",self.s['nameOfDims']
        print "NormDimInd:",self.s['normDimInd']
        print "DimLengths:",self.s['lengthOfDims']
        print "ListOfLists:",self.s['listOfLists']
        return "hello world"



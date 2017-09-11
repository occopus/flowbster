import yaml
import os
import pprint

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
        self.s['hitListAll'] = []
        self.s['isCollector'] = [False] * self.s['maxdim']
        self.s['sizeOfMultiIndexes'] = [0] * self.s['maxdim']
        self.s['convIndSingleToMulti'] = [0] * self.s['maxdim']
        self.s['convIndMultiToSingle'] = [0] * self.s['maxdim']
        self.s['collIndTable'] = [0] * self.s['maxdim']

        return

    def getNormIndexList(self,posList):
        normIndexList = [-1] * self.s['maxdim']
        for index,item in enumerate(self.s['normDimInd']):
            normIndexList[index] = posList[item]
        return normIndexList

    def addItemCheck(self,value,posList):
        hit = True
        inputIndexList = [0] * self.s['maxdim']
        outputIndexList = [0] * self.s['maxdim']
        outputMaxList = [0] * self.s['maxdim']
        if value == self.s['maxdim']:
            for index in range(self.s['numOfDims']):
                if self.s['isCollector'][index]:
                    singleIndex = posList[index]
                    multiIndex = self.s['convIndSingleToMulti'][index][posList[index]]
                    if len(multiIndex)>1:
                        collValue = self.getItemInCollTable(self.s['collIndTable'][index],multiIndex)
                    else:
                        collValue = self.getItemInCollTable(self.s['collIndTable'][index],[0])
                    sizeOfMultiIndexes = self.s['sizeOfMultiIndexes'][index]
                    outputMaxList[index] = sizeOfMultiIndexes
                    maxCollValue = sizeOfMultiIndexes[len(sizeOfMultiIndexes)-1]
                    if collValue < maxCollValue:
                        hit = False
                    else:
                        allIndexes = []
                        for m in range(maxCollValue):
                            multiIndexCounter = multiIndex[0:len(multiIndex)-1]+[m] 
                            allIndexes = allIndexes+[self.convMultiToSingleIndex(self.s['convIndMultiToSingle'][index],multiIndexCounter)]
                        inputIndexList[index] = allIndexes
                        if len(multiIndex)>1:
                            outputIndexList[index] = multiIndex[0:len(multiIndex)-1]
                            outputMaxList[index] = sizeOfMultiIndexes[0:len(sizeOfMultiIndexes)-1]
                        else:
                            outputIndexList[index] = [0]
                            outputMaxList[index] = [1]
                else:
                    inputIndexList[index] = posList[index]
                    outputMaxList[index] = self.s['sizeOfMultiIndexes'][index]
                    outputIndexList[index] = self.s['convIndSingleToMulti'][index][posList[index]]
            if hit:
                if inputIndexList not in self.s['hitListAll']:
                    self.s['hitListAll'].append(inputIndexList)
                    hititem={}
                    hititem['inp_file_indxs']=inputIndexList
                    hititem['out_file_indxs_detailed']=outputIndexList
                    hititem['out_file_maxs_detailed']=outputMaxList
                    L = self.mergeMultiPathIndexes(outputIndexList,outputMaxList)
                    hititem['out_file_indxs']=L[0]
                    hititem['out_file_maxs']=L[1]
                    self.s['hitList'].append(hititem)
        return

    def addItemScanner(self,posList,dimIndex,itemIndex,elist,deepness):
        #print "DL:",posList,"DI:",dimIndex," II:",itemIndex," DEEP:",deepness," EL:",elist
        if dimIndex > 0:
            for index, item in enumerate(elist):
                posList[self.s['numOfDims']-deepness]=index
                self.addItemScanner(posList,dimIndex-1,itemIndex,elist[index],deepness-1)
        if dimIndex == 0:
            if deepness == 1:
                elist[itemIndex]+=1
                posList[self.s['numOfDims']-deepness]=itemIndex
                self.addItemCheck(elist[itemIndex],posList)
            else:
                posList[self.s['numOfDims']-deepness]=itemIndex
                self.addItemScanner(posList,dimIndex-1,itemIndex,elist[itemIndex],deepness-1)
        if dimIndex < 0:
            if deepness == 1:
                for index, item in enumerate(elist):
                    elist[index] +=1
                    posList[self.s['numOfDims']-deepness]=index
                    self.addItemCheck(elist[index],posList)
            else:
                for index, item in enumerate(elist):
                    posList[self.s['numOfDims']-deepness]=index
                    self.addItemScanner(posList,dimIndex-1,itemIndex,elist[index],deepness-1)
        return

    def convMultiToSingleIndex(self,L,ind):
        return self.convMultiToSingleIndex(L[ind[0]], ind[1:]) if len(ind) > 1 else L[ind[0]]

    def addItemToMultiIndexTable(self,multiIndTable,itemIndex,indexList,deepness):
        if deepness+1<len(indexList):
            self.addItemToMultiIndexTable(multiIndTable[indexList[deepness]],itemIndex,indexList,deepness+1)
        else:
            multiIndTable[indexList[deepness]]=itemIndex
        return
    
    def addItem(self,name,itemIndex,indexList):
        #print "NAME:",name,"ITEM:",itemIndex,"LIST:",indexList
        dimIndex = self.s['nameOfDims'].index(name)
        self.s['convIndSingleToMulti'][dimIndex][itemIndex] = indexList
        self.addItemToMultiIndexTable(self.s['convIndMultiToSingle'][dimIndex],itemIndex,indexList,0)
        if self.s['isCollector'][dimIndex] :
            if len(indexList)>1:
                self.incrItemInCollTable(self.s['collIndTable'][dimIndex],indexList)
            else:
                self.incrItemInCollTable(self.s['collIndTable'][dimIndex],[0])

        #print "=== add item ",name,"(",dimIndex,") at position ",itemIndex,"."
        if dimIndex >= self.s['numOfDims']:
            print "ERROR: given dim (",dimIndex,") is greater than actual(",self.s['numOfDims'],") !"
        else:
            posList = [-1] * self.s['numOfDims']
            self.addItemScanner(posList,dimIndex,itemIndex,self.s['listOfLists'],self.s['numOfDims'])

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
        return True if name in self.s['nameOfDims'] else False

    def initNdimList(self,countList,value):
        return [self.initNdimList(countList[1:],value) if len(countList) > 1 else value for _ in range(countList[0])]

    def incrItemInCollTable(self, L, ind):
        #print "incrItemInCollTable: L:",L,"ind:",ind
        if(len(ind) > 2): 
            return self.incrItemInCollTable(L[ind[0]], ind[1:]) 
        else: 
            L[ind[0]] += 1
            return L[ind[0]]

    def getItemInCollTable(self, L, ind):
        return self.getItemInCollTable(L[ind[0]], ind[1:]) if len(ind) > 2 else L[ind[0]]
    
    def addDim(self,name,length,normDimInd,isCollector,countList):
        #print "=== add dim \"",name,"\" width length of ",length,"."
        if self.s['numOfDims'] < self.s['maxdim'] :
            self.s['numOfDims']+=1
            self.s['nameOfDims'][self.s['numOfDims']-1]=name
            self.s['normDimInd'][self.s['numOfDims']-1]=normDimInd
            self.s['lengthOfDims'][self.s['numOfDims']-1]=length
            self.s['isCollector'][self.s['numOfDims']-1]=isCollector
            if self.s['numOfDims'] == 1:
                self.s['listOfLists'] = [0] * length
                self.s['maxsize'] = length
            else:
                self.expandListByOneDim(self.s['listOfLists'],self.s['numOfDims'],length)
                self.s['maxsize'] = self.s['maxsize'] * length

            self.s['sizeOfMultiIndexes'][self.s['numOfDims']-1]=countList
            self.s['convIndSingleToMulti'][self.s['numOfDims']-1]=[0] * length
            self.s['convIndMultiToSingle'][self.s['numOfDims']-1] = self.initNdimList(countList,-1)
            if isCollector :
                if len(countList)>1:
                    self.s['collIndTable'][self.s['numOfDims']-1] = self.initNdimList(countList[0:len(countList)-1],0)
                else:
                    self.s['collIndTable'][self.s['numOfDims']-1] = [0]

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

    def getHitListAll(self):
        return self.s['hitListAll']

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
        self.s['hitListAll'] = []
        self.s['isCollector'] = [False] * self.s['maxdim']
        self.s['sizeOfMultiIndexes'] = [0] * self.s['maxdim']
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
        print "isCollector:",self.s['isCollector']
        print "sizeOfMultiIndexes:",self.s['sizeOfMultiIndexes']
        print "convIndSingleToMulti:",self.s['convIndSingleToMulti']
        print "convIndMultiToSingle:",self.s['convIndMultiToSingle']
        print "collIndTable:",self.s['collIndTable']
        print "HITList:"
        pprint.pprint(self.s['hitList'])
        print "LENGTH:",len(self.s['hitList'])
        print "HITListAll:"
        pprint.pprint(self.s['hitListAll'])
        print "LENGTH:",len(self.s['hitListAll'])
        return 
        
    def addAllItemsToAPort(self,portname,maxindexlist):
        sum = 1
        for i in maxindexlist:
            sum *= i
        indexlist = [0] * len(maxindexlist)
        for index in range(sum):
            #print "=== Adding item ",portname,",",index,",",indexlist," ===="
            self.addItem(portname,index,indexlist[:])
            #print "=== After item ",portname,",",index," ===="
            #self.dump()
            indexlist[len(indexlist)-1]+=1
            for indexforindexlist in range(len(indexlist)-1,0,-1):
                if indexlist[indexforindexlist]>=maxindexlist[indexforindexlist]:
                    indexlist[indexforindexlist]=0
                    indexlist[indexforindexlist-1]+=1
        return
    
    def mergeMultiPathIndexes(self,indList,maxList):
        #print "INDLIST:",indList,"MAXLIST:",maxList
        maxlist = []
        indlist = []
        for portIndex,port in enumerate(maxList):
            maxlist.append([])
            indlist.append([])
            for psIndex,ps in enumerate(maxList[portIndex]):
                if maxList[portIndex][psIndex] > 1:
                    maxlist[portIndex].append(maxList[portIndex][psIndex])
                    indlist[portIndex].append(indList[portIndex][psIndex])
        dimmax = 1
        for item in maxlist:
            if dimmax < len(item):
                dimmax = len(item)
        mergeMaxList = [1] * dimmax
        mergeIndList = [1] * dimmax
        for dimindex in range(dimmax):
            sum = multiplier = 1
            indsum = 0
            for index,item in enumerate(maxlist):
                if len(item)-dimindex-1>=0:
                    sum *= item[len(item)-dimindex-1]
                    indsum += multiplier*indlist[index][len(item)-dimindex-1]
                    multiplier = multiplier*maxlist[index][len(item)-dimindex-1]
            mergeMaxList[dimmax-dimindex-1]=sum
            mergeIndList[dimmax-dimindex-1]=indsum
        return [mergeIndList,mergeMaxList]



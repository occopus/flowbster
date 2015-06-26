from ndimCollector import ndimCollector
import pprint

class ndimTester:

    def __init__ (self,maxnode):
        self.s={}
        self.s['maxnodenumber'] = maxnode
        self.s['nodenumber'] = 0
        self.s['nodelist'] = [0] * self.s['maxnodenumber']
        self.s['nodename'] = [0] * self.s['maxnodenumber']
        self.s['inputportcounter'] = [0] * self.s['maxnodenumber']
        self.s['inputportname'] = [0] * self.s['maxnodenumber']
        self.s['inputportiscoll'] = [0] * self.s['maxnodenumber']
        self.s['outputportcounter'] = [0] * self.s['maxnodenumber']
        self.s['outputportname'] = [0] * self.s['maxnodenumber']
        self.s['outputportgen'] = [0] * self.s['maxnodenumber']
        self.s['maxinpmatrix'] = [0] * self.s['maxnodenumber']
        self.s['links'] = [0] * self.s['maxnodenumber']
        self.s['simulated'] = [0] * self.s['maxnodenumber']
        return

    def create_node(self,nodename,maxport):
        index = self.s['nodenumber']
        self.s['nodelist'][index] = ndimCollector(maxport)
        self.s['nodename'][index] = nodename
        self.s['maxinpmatrix'][index] = [0] * maxport
        self.s['inputportname'][index] = [0] * maxport
        self.s['outputportname'][index] = [0] * maxport
        self.s['inputportiscoll'][index] = [0] * maxport
        self.s['outputportgen'][index] = [1] * maxport
        self.s['inputportcounter'][index] = 0
        self.s['outputportcounter'][index] = 0
        self.s['links'][index] = [-1] * maxport
        self.s['simulated'][index] = [False] * maxport
        self.s['nodenumber']+=1
        return index

    def create_inputport(self,nodename,portname,isCollector):
        index = self.s['nodename'].index(nodename)
        portindex = self.s['inputportcounter'][index]
        self.s['inputportname'][index][portindex] = portname
        self.s['inputportiscoll'][index][portindex] = isCollector
        self.s['inputportcounter'][index]+=1
        return

    def create_outputport(self,nodename,portname,gencount):
        index = self.s['nodename'].index(nodename)
        portindex = self.s['outputportcounter'][index]
        self.s['outputportname'][index][portindex] = portname
        self.s['outputportgen'][index][portindex] = gencount
        self.s['outputportcounter'][index]+=1
        return

    def create_link(self,srcnodename,targetnodename,targetinputname):
        srcnodeind = self.s['nodename'].index(srcnodename)
        trgnodeind = self.s['nodename'].index(targetnodename)
        trginpind = self.s['inputportname'][trgnodeind].index(targetinputname)
        self.s['links'][trgnodeind][trginpind] = srcnodeind
        return

    def feed_input(self,nodename,portname,maxinpmatrix):
        nindex = self.s['nodename'].index(nodename)
        pindex = self.s['inputportname'][nindex].index(portname)
        self.s['maxinpmatrix'][nindex][pindex]=maxinpmatrix

    def calcmax(self,inpmatrix):
        sum=1
        for i in inpmatrix:
            sum *= i
        return sum

    def is_all_port_simulated(self,nindex):
        done = True
        for pindex, portname in enumerate(self.s['inputportname'][nindex]):
            if not self.s['simulated'][nindex][pindex]:
                done = False
        return done

    def simulate_onenode(self,nodename):
        nindex = self.s['nodename'].index(nodename)
        for pindex, portname in enumerate(self.s['inputportname'][nindex]):
            if not self.s['simulated'][nindex][pindex]:
                inpmatrix = self.s['maxinpmatrix'][nindex][pindex]
                isColl = self.s['inputportiscoll'][nindex][pindex]
                trg = self.s['nodelist'][nindex]
                if type(inpmatrix) is list:
                    print "Simulating node \"",nodename,"\" at port \"",portname,"\""
                    maxitems = self.calcmax(inpmatrix)
                    trg.addDim(portname,maxitems,pindex,isColl,inpmatrix)
                    trg.addAllItemsToAPort(portname,self.s['maxinpmatrix'][nindex][pindex])
                    self.s['simulated'][nindex][pindex] = True
                else:
                    srcnodeid = self.s['links'][nindex][pindex]
                    if srcnodeid>=0 and self.is_all_port_simulated(srcnodeid):
                        print "Simulating node \"",nodename,"\" at port \"",portname,"\" from source \"",self.s['nodename'][srcnodeid],"\""
                        src = self.s['nodelist'][srcnodeid]
                        hl = src.getHitList()
                        psgen = self.s['outputportgen'][srcnodeid][0]
                        if psgen == 1:
                            print "No PS node."
                            maxitems = len(hl)
                            trg.addDim(portname,len(hl),pindex,isColl,hl[0]['outputmax'])
                            for hlindex,hlitem in enumerate(hl):
                                trg.addItem(portname,hlindex,hlitem['outputind'])
                            self.s['simulated'][nindex][pindex] = True
                        else:
                            print "PS node."
                            maxitems = len(hl) * psgen
                            maxindexes = hl[0]['outputmax'][:]
                            maxindexes.append(psgen)
                            hlindex = 0
                            trg.addDim(portname,maxitems,pindex,isColl,maxindexes)
                            L=[0] * maxitems
                            for hlitem in hl:
                                maxindexes = hlitem['outputmax'][:]
                                maxindexes.append(psgen)
                                for i in range(psgen):
                                    indexes = hlitem['outputind'][:]
                                    indexeslen = len(indexes)
                                    indexes.append(i)
                                    L[hlindex]=indexes
                                    print "PSOUT c:",hlindex,"item: ",indexes
                                    trg.addItem(portname,hlindex,indexes)
                                    hlindex+=1
                            print "PSout:",L
                            self.s['simulated'][nindex][pindex] = True
        return

    def dump(self):
        for index,node in enumerate(self.s['nodelist']):
            if index<self.s['nodenumber']:
                #node.dump()
                self.s['nodename']
                print "---->NODE: ",self.s['nodename'][index]
                hl = node.getHitList()
                numofrun = len(hl)
                print "-> run: ",numofrun
                print "-> out: ",numofrun*self.s['outputportgen'][index][0]
                print "-> hitlist: "
                pprint.pprint(hl)
                



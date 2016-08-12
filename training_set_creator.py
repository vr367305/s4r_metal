import numpy as np
from metal_patch_selector import *

class TrainingSetCreator:

    def __init__(self, names, raw_data, regions, patch_dim, target_dict,getrotated=False):
        '''
        names: list of strings which are the names of the datasets (to enforce an order)
        raw_data: dictionary with names as keys and images as values
        regions: dictionary of tuples (x1,y1,x2,y2) which is the rectangle selection
        patch_dim: a integer which represents the square side dimension
        target_dict: dictionary with names as keys and their classification number as value
        '''
        self.data=raw_data
        self.names=names
        self.regions=regions
        self.patch_dim=patch_dim
        self.target_dict=target_dict

        self.compileIndexAccumulator()
    
    def getNumberOfAccPatches(self,n):
        count=0
        i=0
        for key in self.names:
            if i<n:
                i+=1
            else:
                break
            x1,y1,x2,y2=self.regions[key]
            #rectangle = self.data[key][x1:x2, y1:y2]
            nRows=x2-x1+1
            nRowsPatch=nRows-(self.patch_dim-1)
            nCols=y2-y1+1
            nColsPatch=nCols-(self.patch_dim-1)
            count+=nRowsPatch*nColsPatch
            #count+=(rectangle.shape[0]-self.patch_dim+1)*(rectangle.shape[1]-self.patch_dim+1)
        return count
    
    def compileIndexAccumulator(self):
        self.indacc=[]
        for i in range(len(self.names)):
            self.indacc.append(self.getNumberOfAccPatches(i+1))

    def patchBinarySearch(self,i,start,end):
        if(start>=end):
            return start
        if(start+1==end):
            return start if i<=self.indacc[start] else end
        if(self.indacc[(start+end)/2]<i):
            return self.patchBinarySearch(i,((start+end)/2)+1,end)
        return self.patchBinarySearch(i,start,(start+end)/2)

    
    def getPatchesFromDataset(self, datasetindex, indexlist):
        totpatches=self.indacc[0] if datasetindex==0 else self.indacc[datasetindex]-self.indacc[datasetindex-1]
        key=self.names[datasetindex]
        x1,y1,x2,y2=self.regions[key]
        nRows=x2-x1+1
        nRowsPatch=nRows-(self.patch_dim-1)
        nCols=y2-y1+1
        nColsPatch=nCols-(self.patch_dim-1)
        assert totpatches==nRowsPatch*nColsPatch
        for ind in indexlist:
            #assert ind<totpatches
            riga=ind//nColsPatch
            colonna=ind%nColsPatch
            yield self.data[key][x1+riga:x1+riga+self.patch_dim,y1+colonna:y1+colonna+self.patch_dim]
    
    def getPatches(self, indexlist_list):
        for i in range(len(indexlist_list)):
            for patch in self.getPatchesFromDataset(i,indexlist_list[i]):
                yield patch,self.target_dict[self.names[i]]

    def getAllPatches(self):
        indexlist_list=[]
        for i in range(len(self.names)):
            indexlist_list.append(range(self.indacc[0] if i==0 else self.indacc[i]-self.indacc[i-1]))
        for i,j in self.getPatches(indexlist_list):
            yield i,j

if __name__=="__main__":
    #test1
    names=["a","b"]
    raw_data={"a":np.array(range(15)).reshape(3,5),"b":(np.array(range(6))+np.array(100)).reshape(2,3)}
    regions={"a":(0,0,2,4),"b":(0,0,1,2)}
    target_dict={"a":1,"b":2}
    print(raw_data)
    tsc=TrainingSetCreator(["a","b"],raw_data,regions,2,target_dict)
    print(tsc.indacc)
    for i,j in tsc.getAllPatches():
        print(j)
        print(i)
    #test 2
    for i,j in tsc.getPatches([[0,7],[1]]):
        print(j)
        print(i)
    #test 3
    p=PatchSelector("../sample.h5", whitelist=['Argento_13_new4', 'Argento_15_new'], allow_print=False)
    print(p.names)
    regions=p.chooseRegions()
    raw_data=p.data
    target_dict={'Argento_13_new4':13,'Argento_15_new':15}
    tsc=TrainingSetCreator(p.names,raw_data,regions,3,target_dict)
    for i,j in tsc.getAllPatches():
        print(j)
        print(i)
    
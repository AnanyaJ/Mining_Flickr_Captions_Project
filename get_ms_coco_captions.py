from pycocotools.coco import COCO
import numpy as np
from pprint import pprint

dataDir='..'
dataType='train2014'

capFile = '%s/annotations/captions_%s.json'%(dataDir,dataType)
coco_caps=COCO(capFile)

# captions
annIds = coco_caps.getAnnIds()
anns = coco_caps.loadAnns(annIds)
captions = []
for ann in anns:
    captions.append(ann['caption'])

fileOut = open('MS COCO Captions.txt','w')
for caption in captions:
    fileOut.write(caption)
    if caption[-1] != '\n':
        fileOut.write('\n')
fileOut.close()

annFile = '%s/annotations/instances_%s.json'%(dataDir,dataType)
coco=COCO(annFile)
# imgIds = coco.getImgIds()

# category names
cats = coco.loadCats(coco.getCatIds())
catNames = [cat['name'] for cat in cats]
fileOut = open('COCO Categories.txt','w')
for name in catNames:
    fileOut.write(name + '\n')
fileOut.close()

# supercategory names
supCatNames = set([cat['supercategory'] for cat in cats])
fileOut = open('COCO Supercategories.txt','w')
for name in supCatNames:
    fileOut.write(name + '\n')
fileOut.close()

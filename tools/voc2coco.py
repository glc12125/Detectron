import os
import xml.etree.ElementTree as ET
import xmltodict
import json
from xml.dom import minidom
from collections import OrderedDict


HARDHAT_TYPES = ['yellow hardhat', 'red hardhat', 'blue hardhat', 'white hardhat', 'orange hardhat', 'green hardhat', 'n03492922']

def generateVOC2Json(rootDir,xmlFiles):
    attrDict = dict()
    #images = dict()
    #images1 = list()
    attrDict["categories"]=[{"supercategory":"none","id":1,"name":"hardhat"},
                    {"supercategory":"none","id":2,"name":"person"}
                  ]
    images = list()
    annotations = list()
    for pathRoot, dirs, files in os.walk(rootDir):
        image_id = 0
        for file in xmlFiles:
            image_id = image_id + 1
            if file in files:

                #image_id = image_id + 1
                annotation_path = os.path.abspath(os.path.join(pathRoot, file))

                #tree = ET.parse(annotation_path)#.getroot()
                image = dict()
                #keyList = list()
                #doc = xmltodict.parse(open(annotation_path).read())
                tree=ET.parse(annotation_path)
                root = tree.getroot()
                #print doc['annotation']['filename']
                #data = doc['annotation']
                image['file_name'] = file[0:-4] + '.jpg'
                #keyList.append("file_name")
                size = root.find('size')
                if size != None:
                    image['height'] = int(size.find('height').text)
                    #keyList.append("height")
                    image['width'] = int(size.find('width').text)
                    #keyList.append("width")
                else:
                    size = root.find('imagesize')
                    image['height'] = int(size.find('nrows').text)
                    image['width'] = int(size.find('ncols').text)

                image['id'] = image_id
                print("File Name: " + file + " and image_id " + str(image_id))
                images.append(image)
                id1 = 1
                findObject = root.find('object')
                if findObject != None:
                    for obj in root.iter('object'):
                        cls = obj.find('name').text
                        if cls in HARDHAT_TYPES:
                            cls = 'hardhat'
                        for value in attrDict["categories"]:
                            annotation = dict()
                            if cls == value["name"]:
                                annotation["iscrowd"] = 0
                                annotation["image_id"] = image_id
                                xmlbox = obj.find('bndbox')
                                if xmlbox != None:
                                    x1 = int(xmlbox.find('xmin').text)
                                    y1 = int(xmlbox.find('ymin').text)
                                    x2 = int(xmlbox.find('xmax').text) - x1
                                    y2 = int(xmlbox.find('ymax').text) - y1
                                else:
                                    # XML generated using LabelMe
                                    polygon = obj.find('polygon')
                                    x_min = 4000
                                    x_max = 4000
                                    y_min = 0
                                    y_max = 0
                                    for pt in polygon.iter('pt'):
                                        cur_x = int(pt.find('x').text)
                                        cur_y = int(pt.find('y').text)
                                        if cur_x > x_max:
                                            x_max = cur_x
                                        elif cur_x < x_min:
                                            x_min = cur_x
                                        if cur_y > y_max:
                                            y_max = cur_y
                                        elif cur_y < y_min:
                                            y_min = cur_y
                                    x1 = x_min
                                    y1 = y_min
                                    x2 = x_max - x1
                                    y2 = y_max - y1
                                annotation["bbox"] = [x1, y1, x2, y2]
                                annotation["area"] = float(x2 * y2)
                                annotation["category_id"] = value["id"]
                                annotation["ignore"] = 0
                                annotation["id"] = id1
                                annotation["segmentation"] = [[x1,y1,x1,(y1 + y2), (x1 + x2), (y1 + y2), (x1 + x2), y1]]
                                id1 +=1

                                annotations.append(annotation)

                else:
                    print("File: " + file + " doesn't have any object")
                #image_id = image_id + 1

            else:
                print("File: " + file + " not found")


    attrDict["images"] = images
    attrDict["annotations"] = annotations
    attrDict["type"] = "instances"

    #print attrDict
    jsonString = json.dumps(attrDict)
    with open("train.json", "w") as f:
        f.write(jsonString)

trainFile = "/Users/liangchuangu/Development/machine_learning/darknet-traffic/zhongjian/train.txt"
trainXMLFiles = list()
with open(trainFile, "r") as f:
    for line in f:
        fileName = line.strip()
        #print(fileName)
        trainXMLFiles.append(fileName + ".xml")


rootDir = "/Users/liangchuangu/Development/machine_learning/darknet-traffic/zhongjian/Annotations/"
generateVOC2Json(rootDir, trainXMLFiles)

import yolov5
import torch
import yaml
from PIL import Image
import numpy
class Yolo():
    def __init__(self):
        model = yolov5.load('yolov5n.pt')
        # set model parameters
        model.conf = 0.25  # NMS confidence threshold
        model.iou = 0.45  # NMS IoU threshold
        model.agnostic = False  # NMS class-agnostic
        model.multi_label = False  # NMS multiple labels per box
        model.max_det = 1000  # maximum number of detections per image
        self.model = model
        with open("classes.yml", 'r') as stream:
            data_loaded = yaml.safe_load(stream)
        self.classes = data_loaded['names']
        print(data_loaded)
        print("init")
    def run(self,img):
        results  =self.model(img)
        predictions = results.pred[0]
        boxes = predictions[:, :4] # x1, y1, x2, y2
        scores = predictions[:, 4]
        categories = predictions[:, 5]
        return self.parse(categories,boxes)
    def to_cat(self,cat)->str:
        return self.classes[cat]
    def parse(self,categories,boxes):
        
        boxes = boxes.tolist()
        print(len(boxes))
        categories = categories.tolist()
        for idx,box in enumerate(boxes):
            box.append(self.to_cat(categories[idx]))
        return boxes
        



if __name__=="__main__":
    img = 'traffic.jpg'
    pic  =numpy.asarray(Image.open(img))
    yolo = Yolo()
    print(yolo.run(pic))
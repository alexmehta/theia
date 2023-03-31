import yolov5
import yaml
from PIL import Image
import numpy

class Yolo():
    """
    This is a yolo object detection class
    Attributes:
        model (class): Holds the internal model
        classes (dict): Dict of classes from classes.yml
    """
    def __init__(self,model_path = 'yolov5n.pt'):
        model = torch.hub.load(r'/home/pi/.cache/torch/hub/ultralytics_yolov5_master', 'custom', path=r'yolov5s.pt', source='local')        # set model parameters
        model.conf = 0.25  # NMS confidence threshold
        model.iou = 0.45  # NMS IoU threshold
        model.agnostic = False  # NMS class-agnostic
        model.multi_label = False  # NMS multiple labels per box
        model.max_det = 1000  # maximum number of detections per image
        self.model = model
        with open("classes.yml", 'r',encoding='utf-8') as stream:
            data_loaded = yaml.safe_load(stream)
        self.classes = data_loaded['names']
        print("init yolo")
    def run(self,img):
        results  =self.model(img)
        predictions = results.pred[0]
        boxes = predictions[:, :4] # x1, y1, x2, y2
        categories = predictions[:, 5]
        return self.parse(categories,boxes)
    def to_cat(self,cat)->str:
        return self.classes[cat]
    def parse(self,categories,boxes):
        boxes = boxes.tolist()
        categories = categories.tolist()
        for idx,box in enumerate(boxes):
            box.append(self.to_cat(categories[idx]))
        return boxes

from yolo.model import YoloNetV3
import yaml
import torch

class Yolo():
    """
    This is a yolo object detection class
    Attributes:
        model (class): Holds the internal model
        classes (dict): Dict of classes from classes.yml
    """
    def __init__(self,model_path = 'yolov5n.pt'):
        model  = YoloNetV3()
        model.load_state_dict(torch.load(model_path))
        with open("classes.yml", 'r',encoding='utf-8') as stream:
            data_loaded = yaml.safe_load(stream)
        self.classes = data_loaded['names']
        self.model = model
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


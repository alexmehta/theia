import numpy as np

def get_boundingboxes(yolo,color_frame):
    color_image = np.asanyarray(color_frame.get_data())
    return yolo.run(color_image)

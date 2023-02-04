import numpy as np;

def get_boundingboxes(color_frame):
    color_image = np.asanyarray(color_frame.get_data())
    return [[90,120,90,120, "dog"],[200,190,200,190, "person"],[300,50,300,50, "chair"]]

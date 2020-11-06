import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches

import xml.etree.ElementTree as ET
import xmltodict

import detecto
from detecto.core import Model
from detecto import utils

import numpy as np

def get_true_bbs(img_path):
    """
    For a given image path, this function gets all the workers' bounding boxes
    Params:
        - img_path (str): path of the image
    """
    
    # Read the XML and convert to dict
    xml_path = img_path.replace(".jpg", ".xml")
    with open(xml_path) as fd:
        doc = xmltodict.parse(fd.read())
    
    # Get bounding boxes coordinates in a dict
    boxes = {}
    try:
        for i, obj in enumerate(doc["annotation"]["object"]):
            xmin = float(obj["bndbox"]["xmin"])
            xmax = float(obj["bndbox"]["xmax"])
            ymin = float(obj["bndbox"]["ymin"])
            ymax = float(obj["bndbox"]["ymax"])
            boxes[i] = (xmin, ymin, xmax, ymax)
            
    except KeyError: # When no object
        pass
    
    except TypeError: # When only 1 object
        xmin = float(doc["annotation"]["object"]["bndbox"]["xmin"])
        xmax = float(doc["annotation"]["object"]["bndbox"]["xmax"])
        ymin = float(doc["annotation"]["object"]["bndbox"]["ymin"])
        ymax = float(doc["annotation"]["object"]["bndbox"]["ymax"])
        boxes[i] = (xmin, ymin, xmax, ymax)
        
    return boxes

def get_predicted_bbs(img_path, model, eps_proba=0.20):
    """
    For a given image path, this function returns all the detected workers' bounding boxes.
    Function that works only with detecto model types
    params:
        - model : detecto model object 
        - eps (float): minimum level of confidence for an object to be detected
    """
    
    image = utils.read_image(img_path)
    labels, bbs, scores = model.predict(image)
    
    # Get only the boxes with scores higher than eps
    mask = scores>=eps_proba
    boxes = {}
    for i, tensor in enumerate(bbs[mask]):
        xmin, ymin, xmax, ymax = tensor.numpy()
        boxes[i] = (xmin, ymin, xmax, ymax)
    
    return boxes


def plot_bbs(img_path, model, eps_proba=0.2):
    """
    This function plots all the bounding boxes detected + the true bounding boxes
    Params:
        - img_path (str): path of the image
        - model (detecto model object) : trained detecto model
        - eps_proba (float): minimum level of confidence that our model must have in order to show the predicted bounding box
    """
    # Plot the image
    fig, ax = plt.subplots(1, figsize=(30,30))
    image = mpimg.imread(img_path)
    ax.imshow(image)
    
    # Get boxes
    true_bbs = get_true_bbs(img_path)
    pred_bbs = get_predicted_bbs(img_path, model, eps_proba)
    
    # Plot the true bounding boxes
    for i in true_bbs.values():
        xmin, ymin, xmax, ymax = i
        w = xmax - xmin
        h = ymax - ymin
        rect = patches.Rectangle((xmin,ymin), w, h, linewidth=3, edgecolor='g', facecolor='none')
        ax.add_patch(rect)
        ax.annotate("worker_true", (xmin,ymin))
        
    for i in pred_bbs.values(): 
        xmin, ymin, xmax, ymax = i
        w, h = xmax - xmin, ymax - ymin
        rect = patches.Rectangle((xmin,ymin), w, h, linewidth=3, edgecolor='b', facecolor='none')
        ax.add_patch(rect)
        ax.annotate("worker_pred", (xmin,ymin))
        
def get_iou(boxA, boxB):
    """
    Given two boxes this function compute the IoU
    Params:
        - boxA (list): list of 4 elements (xmin, ymin, xmax, ymax)
        - boxB (list): list of 4 elements (xmin, ymin, xmax, ymax)
    """
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    # compute the area of intersection rectangle
    interArea = abs(max((xB - xA, 0)) * max((yB - yA), 0))
    if interArea == 0:
        return 0
    
    # compute the area of both the predicted and true rectangles
    boxAArea = abs((boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    boxBArea = abs((boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))
    iou = interArea / float(boxAArea + boxBArea - interArea)

    # return the intersection over union value
    return iou

def get_associate_true_pred_boxes(img_path, model, eps_proba, eps_iou):
    """
    For each true bounding box, this function selects the predicted bounding box with the highest iou
    Params: 
        - img_path (str): path of the image
        - model (detecto model object): trained detecto model
        - eps_proba (float): minimum level of confidence that our model must have in order to show the predicted bounding box
        - eps_iou (float): minimum required level of IOU to consider a predicted bounding box a True Positive
        
    Output: 
        - objects_dico (dict): dictionary where the key corresponds to the true bounding box (list of 4 elements) and 
        the value corresponds to the predicted bounding box (list of 4 elements). If no match, the value is [0,0,0,0]
    """
    
    true_bbs = get_true_bbs(img_path)
    pred_bbs = get_predicted_bbs(img_path, model, eps_proba)
    objects_dico = {}
    for true_box in true_bbs.values():
        max_iou = 0
        max_iou_box = [0, 0, 0, 0]
        for pred_box in pred_bbs.values():
            new_iou = get_iou(true_box, pred_box)
            if new_iou >= eps_iou:
                if new_iou > max_iou:
                    max_iou = new_iou
                    max_iou_box = pred_box
            objects_dico[true_box] = max_iou_box
    return objects_dico

def plot_matching_bbs(img_path, model, eps_proba, eps_iou):
    """
    This function only plots the bounding boxes that match the true bounding boxes
    Params:
        - img_path (str): path of the image
        - model (detecto model object): trained detecto model
        - eps_proba (float): eps_proba (float): minimum level of confidence that our model must have in order to show the predicted bounding box
        - eps_iou (float): minimum required level of IOU to consider a predicted bounding box a True Positive
    """
    # Plot the image
    fig, ax = plt.subplots(1, figsize=(30,30))
    image = mpimg.imread(img_path)
    ax.imshow(image)
    
    # Get boxes
    objects_dico = get_associate_true_pred_boxes(img_path, model, eps_proba, eps_iou)
    
    # Plot the true bounding boxes
    for i in objects_dico.items():
        xmin, ymin, xmax, ymax = i[0]
        w = xmax - xmin
        h = ymax - ymin
        rect = patches.Rectangle((xmin,ymin), w, h, linewidth=3, edgecolor='g', facecolor='none')
        ax.add_patch(rect)
        ax.annotate("worker_true", (xmin,ymin))
        
    for i in objects_dico.items():
        xmin, ymin, xmax, ymax = i[1]
        w = xmax - xmin
        h = ymax - ymin
        rect = patches.Rectangle((xmin,ymin), w, h, linewidth=3, edgecolor='b', facecolor='none')
        ax.add_patch(rect)
        ax.annotate("worker_pred", (xmin,ymin))
    
    return objects_dico
        
def get_mean_iou(img_path, model, eps_proba, eps_iou):
    """
    Given a specific image, this function returns the mean IOU.
    Params:
        - img_path (str): path of the image
        - model (detecto model object): trained detecto model
        - eps_proba (float): eps_proba (float): minimum level of confidence that our model must have in order to show the predicted bounding box
        - eps_iou (float): minimum required level of IOU to consider a predicted bounding box a True Positive
    """
    
    boxes = get_associate_true_pred_boxes(img_path, model, eps_proba, eps_iou)
    ious = []
    for box in boxes.items():
        iou = get_iou(box[0], box[1])
        ious.append(iou)
    
    mean_iou = np.mean(ious)
    return mean_iou
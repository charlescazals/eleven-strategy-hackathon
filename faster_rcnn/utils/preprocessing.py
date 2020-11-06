import xml.etree.ElementTree as ET
import json

def get_kwargs_xml_worker(json_path, 
                   folder_name="images"
                  ):
    """
    Params:
        - json_path (str): path of the json file
        - folder_name (str): name of the folder where the images will be located (only IMPORTANT for imageai, 
        else we can put anything)
        
    Returns: 
        - kwg (dict)
    """
    # Convert json to dict
    data = json.load(open(json_path))
    j = 0
    
    # Get objects only with rectangles
    objs = data["objects"]
    objs_rect = {}
    for obj in objs:
        if obj["classTitle"]=="People":
            
            # Check bounding box is not a point
            pts = obj["points"]["exterior"]
            xs = [i[0] for i in pts]
            ys = [i[1] for i in pts]
            if min(xs)!=max(xs) or min(ys)!=max(ys):
                objs_rect[j] = obj
                j += 1
            else:
                print("bounding box=point : ", json_path)
            
    # Get kwargs for image
    kwg = {}
    kwg["folder_name"] = folder_name
    kwg["file_name"] = json_path.replace(".json", "").split("/")[-1]
    kwg["path_name"] = "/home/jovyan/chronsite/"
    kwg["w"] = data["size"]["width"]
    kwg["h"] = data["size"]["height"]
    kwg["d"] = 3
    kwg["objects"] = {}
    
    # Get kwargs for each object in image
    for i, obj in enumerate(objs_rect.values()):
        key = "object_"+str(i)
        kwg["objects"][key] = {}
        kwg["objects"][key]["object_name"] = "worker"
        
        # Get box dimension
        pts = obj["points"]["exterior"]
        xs = [i[0] for i in pts]
        ys = [i[1] for i in pts]
        
        kwg["objects"][key]["xmin"] = min(xs)
        kwg["objects"][key]["xmax"] = max(xs)
        kwg["objects"][key]["ymin"] = min(ys)
        kwg["objects"][key]["ymax"] = max(ys)
        kwg["objects"][key]["truncated"] = 0
        kwg["objects"][key]["difficult"]= 0
    
    return kwg

def create_xml(output_path, **kwargs):
    
    """
    This function create an xml given keyword arguments.
    Params:
        - output_path (str): directory path of where we want to write our xml file
        - kwargs (dict): all the elements to write in the xml
    """
    
    # convert all to string
    kwargs = json.loads(json.dumps(kwargs), parse_int=str)
    
    # Define structure
    annot = ET.Element('annotation')
    folder = ET.SubElement(annot, 'folder')
    filename = ET.SubElement(annot, 'filename')
    path = ET.SubElement(annot, 'path')
    size = ET.SubElement(annot, 'size')
    width = ET.SubElement(size, 'width')
    height = ET.SubElement(size, 'height')
    depth = ET.SubElement(size, 'depth')
    
    for detected_obj in kwargs["objects"].values():
        # Structure
        obj = ET.SubElement(annot, 'object')
        name = ET.SubElement(obj, 'name')
        pose = ET.SubElement(obj, 'pose')
        trunc = ET.SubElement(obj, 'truncated')
        diff = ET.SubElement(obj, 'difficult')
        bndbox = ET.SubElement(obj, 'bndbox')
        xmin = ET.SubElement(bndbox, 'xmin')
        ymin = ET.SubElement(bndbox, 'ymin')
        xmax = ET.SubElement(bndbox, 'xmax')
        ymax = ET.SubElement(bndbox, 'ymax')
        
        # Values
        name.text = detected_obj["object_name"]
        trunc.text = detected_obj["truncated"]
        diff.text = detected_obj["difficult"]
        xmin.text = detected_obj["xmin"]
        xmax.text = detected_obj["xmax"]
        ymin.text = detected_obj["ymin"]
        ymax.text = detected_obj["ymax"]
    
    # Write values
    folder.text = kwargs["folder_name"]
    filename.text = kwargs["file_name"]
    path.text = kwargs["path_name"]
    width.text = kwargs["w"]
    height.text = kwargs["h"]
    depth.text = kwargs["d"]

    # create a new XML file with the results
    tree = ET.ElementTree(annot)
    file_name = kwargs["file_name"].split("/")[-1].replace(".jpg", "")
    tree.write(output_path + "/" + file_name + ".xml")
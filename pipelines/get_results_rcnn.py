from detecto import core, utils, visualize
import glob
import json
import os
import PIL

class GetResultsTestSetPipeline:

    def launch(self) -> None:
        print('Get Results TestSet launched')
        model = self.extract()
        res = self.transform(model)
        self.load(res, test_set_dir = "Detection_Test_Set_Img/")
        print('Get Results TestSet ended\n')
    
    @staticmethod
    def extract():
        model = core.Model.load("faster_rcnn/final_model.pth", ["worker"])
        cmd1 = "wget -O tarball.tar https://oneleven-my.sharepoint.com/:u:/g/personal/ugo_mantel_eleven-strategy_com/EUlJJHa8exhDg8hT6nf0fhcBGb-VbRpoQ5PUcQDwGOKLEQ?download=1"
        cmd2 = "tar -xvf tarball.tar"
        cmd3 = "rm tarball.tar"
        os.system(cmd1)
        os.system(cmd2)
        os.system(cmd3)
        return model
    
    @staticmethod
    def transform(model) -> dict:
        test_imgs = glob.glob("Detection_Test_Set_Img/*.jpg")
        if len(test_imgs)==0:
            raise Exception("Test Set not downloaded")
        res = {}
        for img in test_imgs:
            image = utils.read_image(img)
            image_name = img.split("/")[-1]
            predictions = model.predict(image)
            labels, boxes, scores = predictions
            mask = scores>=0.2
            res[image_name] = {}
            res[image_name]["boxes"] = boxes[mask].numpy().tolist()
            res[image_name]["scores"] = scores[mask].numpy().tolist()
            print(image_name + " : done")
        return res
        
    @classmethod
    def load(cls, res:dict, test_set_dir:str) -> None:
        cls.res_to_json(res, test_set_dir)

    ##################
    # Helper methods #
    ##################
    
    @staticmethod
    def res_to_json(res: dict, test_set_dir: str) -> None:
        """
        Goal: convert the res dictionary to the json with the coco format
        Input:
            - res (dict): {"jpg_name_0": {"boxes": [], "scores": []}, 
                                "jpg_name_1":{"boxes":[] , "scores":[]}, ... }
            - test_set_dir (str): path of the directory where test images are stored
        Output:
            - json (coco format)
        """
        coco_json = {}

        # Information related to the whole dataset
        coco_json["info"] = {"description": "chronsite", 
                             "year": 2020}
        coco_json["licences"] = []
        coco_json["categories"] = [{"supercategory": "none", 
                                    "id":1, 
                                    "name": "worker"}]

        # Information per image
        imgs = [i for i in res.keys()]
        coco_json["images"] = []
        coco_json["annotations"] = []
        idx_annot = 0
        for idx_img, img in enumerate(imgs):
            # Information about the image
            img_name = img.split("/")[-1]
            image = PIL.Image.open(test_set_dir + img)
            w, h = image.size
            dico = {"file_name": img, 
                    "height": h, 
                    "width": w,
                    "id": idx_img}
            coco_json["images"].append(dico)

            # Information about annotations related to that image
            img_detections = res[img_name]
            tot_boxes = len(img_detections["boxes"])
            if tot_boxes==0:
                pass
            else:
                for box in range(tot_boxes):
                    xmin, ymin, xmax, ymax = img_detections["boxes"][box]
                    w = xmax - xmin
                    h = ymax - ymin
                    dico_annot = {"id": idx_annot,
                                  "bbox": [xmin, ymax, w, h],
                                  "image_id": idx_img,
                                  "segmentation": [],
                                  "area": w*h,
                                  "iscrowd": 0,
                                 "category_id": 1} # Only workers in our detection model
                    coco_json["annotations"].append(dico_annot)
                    idx_annot += 1

        # Convert to json
        json.dump(coco_json, open("test_set_results.json", "w"))
    

if __name__ == '__main__':
    GetResultsTestSetPipeline().launch()

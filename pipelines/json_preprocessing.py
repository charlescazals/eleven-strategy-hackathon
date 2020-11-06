import glob
import json
import os
import pickle
from typing import List, Tuple


class JsonPreprocessingPipeline:
    
    def launch(self,
               path_jsons: str = 'Detection_*/*/*.json'
               ) -> None:
        print('JsonPreprocessing launched')
        boxes_processed, zones_processed, data_jsons = self.extract(path_jsons)
        boxes_processed, zones_processed = self.transform(
            boxes_processed, zones_processed, data_jsons
        )
        self.load(boxes_processed, zones_processed)
        print('JsonPreprocessing ended\n')

    @staticmethod
    def extract(path_jsons: str) -> Tuple[dict]:
        boxes_processed_file = 'intermediate_process/boxes_processed.pickle'
        if not os.path.isfile(boxes_processed_file):
            boxes_processed = {}
        else:
            with open(boxes_processed_file, 'rb') as file:
                boxes_processed = pickle.load(file)
        
        zones_processed_file = 'intermediate_process/zones_processed.pickle'
        if not os.path.isfile(zones_processed_file):
            zones_processed = {}
        else:
            with open(zones_processed_file, 'rb') as file:
                zones_processed = pickle.load(file)
        
        data_jsons = {
            str(json_): json.load(open(json_))
            for json_ in glob.glob(path_jsons)
        }
        
        return (
            boxes_processed, zones_processed, data_jsons
        )

    @classmethod
    def transform(cls,
                  boxes_processed: dict,
                  zones_processed: dict,
                  data_jsons: dict) -> Tuple[dict]:
        return (
            cls.transform_boxes(boxes_processed, data_jsons),
            cls.transform_zones(zones_processed, data_jsons)
        )

    @staticmethod
    def load(boxes_processed: dict, zones_processed: dict) -> None:
        os.makedirs('intermediate_process', exist_ok=True)
        with open('intermediate_process/boxes_processed.pickle', 'wb') as f:
            pickle.dump(boxes_processed, f, protocol=pickle.HIGHEST_PROTOCOL)
        with open('intermediate_process/zones_processed.pickle', 'wb') as f:
            pickle.dump(zones_processed, f, protocol=pickle.HIGHEST_PROTOCOL)
            
    ##################
    # Helper methods #
    ##################
    
    @staticmethod
    def transform_boxes(boxes_processed:dict, data_jsons: dict) -> dict:
        for picture in data_jsons.keys():
            data = data_jsons[picture]
            mixer_truck_boxes = []
            people_boxes = []
            for obj in data['objects']:
                points = obj['points']['exterior']
                x_min, y_min = points[0]
                x_max, y_max = points[1]
                coords = [x_min, y_min, x_max, y_max]
                if obj['classTitle'] == 'Mixer_truck':
                    mixer_truck_boxes.append(coords)
                if obj['classTitle'] == 'People':
                    people_boxes.append(coords)
            img_height = data['size']['height']
            img_width = data['size']['width']
            objs = {'Mixer_truck': mixer_truck_boxes, 'People': people_boxes}
            boxes_processed[picture] = (objs, img_height, img_width)
        
        return boxes_processed
    
    @staticmethod
    def transform_zones(zones_processed: dict, data_jsons: List[str]) -> List[tuple]:
        for picture in data_jsons:
            data = data_jsons[picture]
            concrete_pumps_zones = []
            formworks_zones = []
            for obj in data['objects']:
                points = obj['points']['exterior']
                if obj['classTitle'] == 'Concrete_pump_hose':
                    concrete_pumps_zones.append(points)
                if obj['classTitle'] == 'Vertical_formwork':
                    formworks_zones.append(points)
            img_height = data['size']['height']
            img_width = data['size']['width']
            objs = {'Concrete_pump_hose': concrete_pumps_zones,
                    'Vertical_formwork': formworks_zones}
            zones_processed[picture] = (objs, img_height, img_width)
        
        return zones_processed


if __name__ == '__main__':
    JsonPreprocessingPipeline().launch()

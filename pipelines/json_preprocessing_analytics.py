import glob
import json
import os
import pickle
from typing import List, Tuple


class JsonPreprocessingAnalyticsPipeline:
    
    def launch(self,
               path_jsons: str = 'Analytics_*/*/*/*.json'
               ) -> None:
        print('JsonPreprocessingAnalytics launched')
        boxes_processed, zones_processed, data_jsons = self.extract(path_jsons)
        boxes_processed, zones_processed = self.transform(
            boxes_processed, zones_processed, data_jsons
        )
        self.load(boxes_processed, zones_processed)
        print('JsonPreprocessingAnalytics ended\n')

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
        
        data_jsons = {}
        for json_ in glob.glob(path_jsons):
            try:
                data_jsons[str(json_)] = json.load(open(json_, 'rb'))
            except:
                print(json_)

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
    
    @classmethod
    def transform_boxes(cls, boxes_processed: dict, data_jsons: dict) -> dict:
        for picture in data_jsons.keys():
            data = data_jsons[picture]
            if 'people' not in picture:
                continue
            picture = cls._change_name(picture)
            people_boxes = []
            for obj in data['objects']:
                points = obj['points']['exterior']
                x_min, y_min = points[0]
                x_max, y_max = points[1]
                coords = [x_min, y_min, x_max, y_max]
                if obj['classTitle'] == 'People_model':
                    people_boxes.append(coords)
            img_height = data['size']['height']
            img_width = data['size']['width']
            objs = {'People': people_boxes}
            boxes_processed[picture] = (objs, img_height, img_width)
        
        return boxes_processed
    
    @classmethod
    def transform_zones(cls,
                        zones_processed: dict,
                        data_jsons: List[str]) -> List[tuple]:
        for picture in data_jsons:
            data = data_jsons[picture]
            if 'poly' not in picture:
                continue
            picture = cls._change_name(picture)
            horizontal_zones = []
            vertical_zones = []
            rebars_zones = []
            concrete_pumps = []
            for obj in data['objects']:
                encoded_mask = obj['bitmap']
                if obj['classTitle'] in ['Vertical formwork_model',
                                         'Vertical_formwork']:
                    vertical_zones.append(encoded_mask)
                elif obj['classTitle'] in ['Rebars_model',
                                           'Rebars']:
                    rebars_zones.append(encoded_mask)
                elif obj['classTitle'] in ['Horizontal formwork_model',
                                           'Horizontal_formwork']:
                    horizontal_zones.append(encoded_mask)
                elif obj['classTitle'] in ['Concrete pump hose',
                                           'Concrete_pump_hose']:
                    concrete_pumps.append(encoded_mask)
                else:
                    print(obj['classTitle'])
            img_height = data['size']['height']
            img_width = data['size']['width']
            objs = {'Vertical_formwork': vertical_zones,
                    'Horizontal_formwork': horizontal_zones,
                    'Concrete_pump_hose': concrete_pumps,
                    'Rebars': rebars_zones}
            zones_processed[picture] = (objs, img_height, img_width)
        
        return zones_processed
    
    @staticmethod
    def _change_name(picture: str) -> str:
        return (
            picture
            .replace('Analytics_Train_Set/Analytics_Train_Set_Json/poly',
                     'Analytics_Train_Set/Analytics_Train_Set_Img')
            .replace('Analytics_Train_Set/Analytics_Train_Set_Json/people',
                     'Analytics_Train_Set/Analytics_Train_Set_Img')
        )


if __name__ == '__main__':
    JsonPreprocessingAnalyticsPipeline().launch()

import os
import pickle
from typing import List, Tuple

import numpy as np
from shapely.geometry import Polygon

from utils import draw_mask


class ConcretePumpPipeline:

    def launch(self,
               analytics_pattern: str = 'Analytics'
               ) -> None:
        print('ConcretePump launched')
        zones = self.extract()
        pump_by_picture = self.transform(zones, analytics_pattern)
        self.load(pump_by_picture)
        print('ConcretePump ended\n')
    
    @staticmethod
    def extract() -> dict:
        with open('intermediate_process/zones_processed.pickle', 'rb') as file:
            zones_processed = pickle.load(file)
        
        return zones_processed
    
    @classmethod
    def transform(cls, zones: dict, analytics_pattern: str) -> dict:
        pump_by_picture = {}
        for picture in zones:
            if not picture.startswith(analytics_pattern):
                continue
            zones_by_type, height, width = zones[picture]
            extremities = []
            centroids = []
            for pump in zones_by_type['Concrete_pump_hose']:
                mask = draw_mask(pump, height, width)
                extremities.append(cls._get_pump_extremity(mask))
                centroids.append(cls._get_pump_centroid(mask))
            pump_by_picture[picture] = {'extremity': extremities,
                                        'centroid': centroids}
        
        return pump_by_picture
    
    @staticmethod
    def load(pump_by_picture: dict) -> None:
        os.makedirs('intermediate_process', exist_ok = True)
        with open('intermediate_process/pump_key_points.pickle', 'wb') as f:
            pickle.dump(pump_by_picture, f, protocol=pickle.HIGHEST_PROTOCOL)

    ##################
    # Helper methods #
    ##################

    @staticmethod
    def _get_pump_extremity(mask: np.array) -> Tuple[int]:
        last_index = len(mask)-1
        while sum(mask[last_index])==0 and last_index>=0:
            last_index-=1
        if last_index == -1:
            return (None, None)
        
        one_mask = mask[last_index]*range(len(mask[last_index]))
        return (int(round(one_mask[one_mask>0].mean())), last_index)

    @staticmethod
    def _get_pump_centroid(mask: np.array) -> Tuple[float]:
        if (mask==1).sum() == 0:
            return (None, None)
        
        return np.argwhere(mask==1).sum(0)/(mask==1).sum()

if __name__=='__main__':
    ConcretePumpPipeline().launch()

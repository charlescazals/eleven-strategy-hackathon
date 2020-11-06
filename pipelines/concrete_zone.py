import os
import pickle

from utils import draw_mask


class ConcreteZonePipeline:

    def launch(self) -> None:
        print('ConcreteZone launched')
        zones = self.extract()
        masks = self.transform(zones)
        self.load(masks)
        print('ConcreteZone ended\n')
    
    @staticmethod
    def extract() -> dict:
        with open('intermediate_process/zones_processed.pickle', 'rb') as file:
            zones_processed = pickle.load(file)
        
        return zones_processed
    
    @classmethod
    def transform(cls, zones: dict) -> dict:
        mask_by_picture = {}
        for picture in zones.keys():
            masks_by_type = {}
            zones_by_type, height, width = zones[picture]
            for zone_type in zones_by_type.keys():
                masks = []
                for zone in zones_by_type[zone_type]:
                    masks.append(draw_mask(zone, height, width))
                masks_by_type[zone_type] = masks
            mask_by_picture[picture] = (masks_by_type, height, width)
        
        return mask_by_picture

    @staticmethod
    def load(masks: dict) -> None:
        os.makedirs('intermediate_process', exist_ok=True)
        with open('intermediate_process/masks.pickle', 'wb') as f:
            pickle.dump(masks, f, protocol=pickle.HIGHEST_PROTOCOL)

if __name__=='__main__':
    ConcreteZonePipeline().launch()


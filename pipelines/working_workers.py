import os
import pickle
from typing import List, Tuple

import numpy as np

from constants import WORKERS_RANGE_OF_ACTION
from utils import get_typical_size


class WorkingWorkersPipeline:

    def launch(self) -> None:
        print('WorkingWorkers launched')
        boxes, pump = self.extract()
        pump_by_picture = self.transform(boxes, pump)
        self.load(pump_by_picture)
        print('WorkingWorkers ended\n')
    
    @staticmethod
    def extract() -> Tuple[dict]:
        with open('intermediate_process/boxes_processed.pickle', 'rb') as file:
            boxes_processed = pickle.load(file)
        with open('intermediate_process/pump_key_points.pickle', 'rb') as file:
            pump_centers = pickle.load(file)
        
        return boxes_processed, pump_centers
    
    @classmethod
    def transform(cls, boxes: dict, pump: dict):
        pump_by_picture = {}
        cpt = 0
        for picture in pump.keys():
            pump_centers = pump[picture]['extremity']
            try:
                workers = boxes[picture][0]['People']
            except KeyError:
                cpt+=1
                print('no workers for', picture, cpt)
                workers = []
            workers_centers = cls._get_workers_centers(workers)
            typical_range_of_action = (
                get_typical_size(workers)*WORKERS_RANGE_OF_ACTION
            )
            workers_by_pump = {}
            for pump_center in pump_centers:
                previous_workers_nb = -1
                current_workers_nb = 0
                centers = [pump_center]
                while current_workers_nb > previous_workers_nb:
                    working_workers = cls._find_workers_from_centers(
                        centers, workers_centers, typical_range_of_action
                    )
                    previous_workers_nb = current_workers_nb
                    current_workers_nb = len(working_workers)
                    centers = [pump_center, *working_workers]
                workers_by_pump[pump_center] = working_workers
            pump_by_picture[picture] = workers_by_pump
        
        return pump_by_picture

    @staticmethod
    def load(pump_by_picture: dict) -> None:
        os.makedirs('intermediate_process', exist_ok=True)
        with open('intermediate_process/pump_and_workers.pickle', 'wb') as f:
            pickle.dump(pump_by_picture, f, protocol=pickle.HIGHEST_PROTOCOL)

    ##################
    # Helper methods #
    ##################

    @staticmethod
    def _get_workers_centers(workers: List[List[int]]) -> List[int]:
        return [
            [(worker[0]+worker[2])//2, (worker[1]+worker[3])//2]
            for worker in workers
        ]

    @classmethod
    def _find_workers_from_centers(
        cls,
        centers: List[List[int]],
        workers: List[List[int]],
        typical_range_of_action: int
    ) -> List[List[int]]:

        working_workers = []
        for worker in workers:
            if worker in centers:
                working_workers.append(worker)
            elif cls._compute_distance(centers,
                                       worker) <= typical_range_of_action:
                working_workers.append(worker)
        
        return working_workers
    
    @staticmethod
    def _compute_distance(centers: List[List[int]],
                          object_: List[int]) -> float:
        distances = []
        for center in centers:
            if center[0] and center[1]:
                distances.append(np.sqrt(
                    (object_[0]-center[0])**2 + (object_[1]-center[1])**2)
                )
            else:
                distances.append(np.inf)
        
        return min(distances)

if __name__=='__main__':
    WorkingWorkersPipeline().launch()

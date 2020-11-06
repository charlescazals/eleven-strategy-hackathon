import os
import pickle
from typing import List, Tuple

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


class PlotHeatmapPipeline:

    def launch(self) -> None:
        print('PlotHeatmap launched')
        pump_key_points = self.extract()
        xs, ys = self.transform(pump_key_points)
        self.load(xs, ys)
        print('PlotHeatmap ended\n')
    
    @staticmethod
    def extract() -> dict:
        with open('intermediate_process/pump_key_points.pickle', 'rb') as file:
            pump_key_points = pickle.load(file)
        
        return pump_key_points
    
    @staticmethod
    def transform(pump_key_points: dict) -> Tuple[List[int]]:
        xs, ys = [], []
        for figure in pump_key_points.keys():
            for coord in pump_key_points[figure]['extremity']:
                xs.append(coord[0])
                ys.append(1024 - coord[1] if coord[1] is not None else None)
        
        return xs, ys

    @staticmethod
    def load(xs: List[int], ys: List[int]) -> None:
        output_folder = 'output_csv/'
        os.makedirs(output_folder, exist_ok=True)
        fig, ax = plt.subplots(1)
        plt.scatter(xs, ys, c=range(len(xs)))
        ax.add_patch(Rectangle((0, 0), 1280, 1024, fill=False))
        plt.colorbar()
        plt.axis('equal')
        plt.savefig(f'{output_folder}extremity_heatmap.png')

if __name__=='__main__':
    PlotHeatmapPipeline().launch()


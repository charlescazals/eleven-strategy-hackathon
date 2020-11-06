import os
import pickle
from datetime import datetime
from typing import Tuple

import pandas as pd

from utils import get_date_from_picture_name


class PlotWorkerPipeline:

    def launch(self) -> None:
        print('PlotWorker launched')
        workers_by_pump_by_picture, boxes_processed = self.extract()
        pump_workers_series, workers_series = self.transform(workers_by_pump_by_picture, boxes_processed)
        self.load(pump_workers_series, workers_series)
        print('PlotWorker ended\n')
    
    @staticmethod
    def extract() -> Tuple[dict]:
        with open('intermediate_process/pump_and_workers.pickle', 'rb') as file:
            workers_by_pump_by_picture = pickle.load(file)
        with open('intermediate_process/boxes_processed.pickle', 'rb') as file:
            boxes_processed = pickle.load(file)
        
        return workers_by_pump_by_picture, boxes_processed
    
    @classmethod
    def transform(cls, workers_by_pump_by_picture: dict, boxes_processed: dict) -> Tuple[pd.Series]:
        return (
            cls.smooth_df(cls.create_pump_workers_df(workers_by_pump_by_picture)),
            cls.smooth_df(cls.create_workers_df(boxes_processed))
        )
    
    @staticmethod
    def load(pump_workers_series: pd.Series, workers_series: pd.Series) -> None:
        output_folder = 'output_csv/'
        os.makedirs(output_folder, exist_ok=True)
        pump_workers_series.to_csv(f'{output_folder}pump_workers_by_date.csv')
        workers_series.to_csv(f'{output_folder}workers_by_date.csv')

    
    ##################
    # Helper methods #
    ##################

    @staticmethod
    def create_pump_workers_df(workers_by_pump_by_picture: dict) -> pd.Series:
        pump_workers_by_date = {}
        for picture in workers_by_pump_by_picture.keys():
            if not picture.startswith('Analytics'):
                continue
            date = get_date_from_picture_name(picture)
            pump_workers_by_date[date] = sum(
                [len(workers) for workers in workers_by_pump_by_picture[picture].values()]
            )
        
        return pd.Series(pump_workers_by_date).sort_index()
    
    @staticmethod
    def create_workers_df(boxes_processed: dict) -> pd.Series:
        workers_by_date = {}
        for picture in boxes_processed.keys():
            if not picture.startswith('Analytics'):
                continue
            date = get_date_from_picture_name(picture)
            workers_by_date[date] = len(boxes_processed[picture][0]['People'])
        
        return pd.Series(workers_by_date).sort_index()
    
    @staticmethod
    def smooth_df(s: pd.Series, half_range: int = 5) -> pd.Series:
        return pd.DataFrame([
            s.shift(i) for i in range(-half_range, half_range+1)
        ]).transpose().max(axis=1)


if __name__=='__main__':
    PlotWorkerPipeline().launch()

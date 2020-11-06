from .json_preprocessing import JsonPreprocessingPipeline
from .json_preprocessing_analytics import JsonPreprocessingAnalyticsPipeline
from .concrete_pump import ConcretePumpPipeline
from .working_workers import WorkingWorkersPipeline
from .plot_worker import PlotWorkerPipeline
from .plot_heatmap import PlotHeatmapPipeline

pipelines = [
    JsonPreprocessingPipeline,
    JsonPreprocessingAnalyticsPipeline,
    ConcretePumpPipeline,
    WorkingWorkersPipeline,
    PlotWorkerPipeline,
    PlotHeatmapPipeline,
]

"""Feature Selector"""
import logging
from automl.pipeline import PipelineData

import numpy as np

class FeatureSelector:
    """
    Class for feature selection step in pipeline 
    """
    def __init__(self, max_features):
        """
        Parametrs
        ---------
        max_feature : int
            Approximate desired numbers of features
        """
        self._log = logging.getLogger(self.__class__.__name__)
        self.max_features = max_features

    def __call__(self, pipeline_data, context):
        """
        Parametrs
        ---------
        pipeline_data : PipelineData
            Data passed between PipelineStep in pipeline

        context : PiplineContext
            Global context of pipeline

        Returns
        -------
        PipelineData
            PipelineData.dataset contains changed dataset, PipelineData.return_val
            contains unchanged result of validation step 
        """
        mask = np.array([False for _ in range(0, pipeline_data.dataset.data.shape[1])])
        
        # TODO this really should not be used with more than one model
        # Use ChooseBest(1)
        # For seceral models use VotingFeatureSelector
        for value in pipeline_data.return_val:
            model = value.model

            # TODO: CV scorer in hyperopt does not fit models ???
            model.fit(pipeline_data.dataset.data, pipeline_data.dataset.target)

            if hasattr(model, "coef_"):
                f_score = [abs(coef) for coef in model.coef_]
            elif hasattr(model, "feature_importances_",):
                f_score = [abs(feature_importances) for feature_importances in model.feature_importances_]
            else: 
                f_score = None

            if f_score is not None and pipeline_data.dataset.data.shape[1] > self.max_features:
                threshold = sorted(f_score)[-self.max_features]
                mask = mask + np.array([score > threshold for score in f_score])
                self._log.info(f"Removing {sum(mask)} features for model {model.__class__.__name__}")
            else:
                self._log.warn(f"Model {model.__class__.__name__} is not supported by FeatureSelector")
        
        if mask.sum():
            pipeline_data.dataset.data = pipeline_data.dataset.data.compress(mask, axis=1)

        return PipelineData(pipeline_data.dataset, pipeline_data.return_val)
"""Feature Generators"""

import logging
from functools import partial
import random
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from automl.pipeline import PipelineData




class SklearnFeatureGenerator:
    def __init__(self, transformer_class, *args, **kwargs):
        """
        Wrapper for Scikit-Learn Transformers

        Parameters
        ----------
        kwargs:
            keyword arguments are passed to sklearn PolynomialFeatures
        """
        self._log = logging.getLogger(self.__class__.__name__)
        self._transformer = transformer_class(*args, **kwargs)

    def __call__(self, pipeline_data, pipeline_context):
        """
        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            The data.

        pipeline_context: automl.pipeline.PipelineContext
            global context of a pipeline

        Returns
        -------
        X_new : numpy array of shape [n_samples, n_features_new]
            Transformed array.
        """

        pipeline_data.dataset.data = self._transformer.fit_transform(pipeline_data.dataset.data)
        return pipeline_data


class FormulaFeatureGenerator:
    def __init__(self, func_list=['+', '-', '*', '/']):
        """
        Initialize Formula Feature Generator

        Paramets
        --------
        func_list : list of symbols of functions
            In current version func_list may contain only '+', '-', '*', '/'.

        Attributes
        ----------
        _func_map : dict of generating functions
            The function for generation new features

        used_func : set of of symbols of functions
        """
        self.used_func = set(func_list)
        self._func_map = {
            '+': self._sum,
            '-': self._substract,
            '/': self._divide,
            '*': self._multiply,
        }

    def _sum(self, X):
        """
        Add one new feature generated by sum of two random features

        Parametrs
        ---------
        X : np.ndarray, shape [n_samples, n_features]
            The data to transform, row by row.

        Returns
        -------
        XF : np.ndarray shape [n_samples, n_features+1]
            The matrix of features with one new feature
        """
        x, y = self._choose_two_features(X)
        return x + y
    def _substract(self, X):
        """
        Add one new feature generated by substraction of two random features

        Parametrs
        ---------
        X : np.ndarray, shape [n_samples, n_features]
            The data to transform, row by row.

        Returns
        -------
        XF : np.ndarray shape [n_samples, n_features+1]
            The matrix of features with one new feature
        """
        x, y = self._choose_two_features(X)
        return x - y

    def _divide(self, X):
        """
        Add one new feature generated by division of two random features

        Parametrs
        ---------
        X : np.ndarray, shape [n_samples, n_features]
            The data to transform, row by row.

        Returns
        -------
        XF : np.ndarray shape [n_samples, n_features+1]
            The matrix of features with one new feature
        """
        x, y = self._choose_two_features(X)
        return x / y

    def _multiply(self, X):
        """
        Add one new feature generated by multiplication of two random features

        Parametrs
        ---------
        X : np.ndarray, shape [n_samples, n_features]
            The data to transform, row by row.

        Returns
        -------
        XF : np.ndarray shape [n_samples, n_features+1]
            The matrix of features with one new feature
        """
        x, y = self._choose_two_features(X)
        return x * y

    def _choose_two_features(self, X):
        """
        Choose two features from input data

        Parametrs
        ---------
        X : np.ndarray, shape [n_samples, n_features]
            The data

        Returns
        -------
        x, y : Two vectors of selected features
        """
        return X[:, random.randint(0, X.shape[1]-1)].reshape(X.shape[0], 1), \
               X[:, random.randint(0, X.shape[1]-1)].reshape(X.shape[0], 1)

    def __call__(self, pipeline_data, pipeline_context, limit=10):
        """
        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            The data.

        limit : int
            Amount of new features

        pipeline_context: automl.pipeline.PipelineContext
            global context of a pipeline

        Returns
        -------
        XF : numpy array of shape [n_samples, n_features+limit]
            Transformed array.
        """
        if not isinstance(pipeline_data.dataset, np.ndarray):
            X = np.array(pipeline_data.dataset.data)
        else:
            X = pipeline_data.dataset.data

        for _ in range(0, limit):
            new_feature = self._func_map[random.sample(self.used_func, 1)[0]](X)
            if np.isfinite(new_feature).all():
                X = np.append(X, new_feature, axis=1)

        pipeline_data.dataset.data = X
        return pipeline_data 


PolynomialGenerator = partial(SklearnFeatureGenerator, PolynomialFeatures)

from sklearn.cluster import (
    KMeans, AffinityPropagation, MeanShift,
    SpectralClustering, AgglomerativeClustering, DBSCAN
)
import numpy as np
from models.solution import Solution
from utils import calculate_objective, find_cluster_hub_nodes


class ClusteringService:
    """
    @class ClusteringService
    @brief Wraps scikit-learn clustering algorithms and computes hubs/objective.

    The `ClusteringService` class provides an interface for applying various clustering algorithms 
    (such as KMeans, DBSCAN, and others) and computes the hubs and objective value for the clustering result.
    """

    def cluster(self, method: str, df, **params) -> Solution:
        """
        @brief Applies a clustering algorithm and computes hubs and objective value.

        This method applies the selected clustering algorithm to the given dataset and computes the hubs 
        (data points closest to cluster centroids) and the objective value (sum of squared distances to hubs).

        @param method: The clustering algorithm method to be applied (e.g., 'kmeans', 'affinity', etc.).
        @param df: The input data (pandas DataFrame).
        @param params: Additional parameters for the clustering algorithm.
        @return: A `Solution` object containing the clustering results, including labels, hubs, and objective.
        @throws ValueError: If an unknown clustering method is specified.
        """
        # Extract data array from DataFrame
        arr = df.values

        # Initialize model based on selected method
        if method == 'kmeans':
            model = KMeans(**params)
        elif method == 'affinity':
            model = AffinityPropagation(**params)
        elif method == 'meanshift':
            model = MeanShift(**params)
        elif method == 'spectral':
            model = SpectralClustering(**params)
        elif method == 'hierarchical':
            model = AgglomerativeClustering(**params)
        elif method == 'dbscan':
            model = DBSCAN(**params)
        else:
            raise ValueError(f"Unknown clustering method: {method}")

        # Fit the model and predict labels
        labels = model.fit_predict(arr)
        # Filter out noise if DBSCAN is used (label -1 represents noise)
        unique = [l for l in np.unique(labels) if l != -1]

        # Compute hubs: data points closest to cluster centroids
        hubs, hub_indices = find_cluster_hub_nodes(arr, labels, unique)

        # Compute objective: sum of squared distances to hubs
        objective = calculate_objective(arr, labels, hubs, unique)

        # Prepare Solution object to store clustering results
        sol = Solution(data=df)
        sol.labels = labels
        sol.cluster_labels = unique
        sol.hubs = hubs
        sol.hub_indices = hub_indices
        sol.objective = objective
        return sol

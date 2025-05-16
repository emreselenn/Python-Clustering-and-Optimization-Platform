import numpy as np
import matplotlib.pyplot as plt

def calculate_objective(data, labels, hubs, cluster_labels):
    """
    @brief Calculates the objective value for a clustering solution.

    This function calculates the objective value by computing the sum of squared distances 
    between the data points and their respective hubs (cluster centers). The objective is used
    to evaluate the quality of a clustering solution.

    @param data: The data points (numpy array).
    @param labels: The labels of each data point indicating the assigned cluster.
    @param hubs: The coordinates of the cluster hubs (centroids).
    @param cluster_labels: The unique cluster labels for the clustering result.
    @return: The objective value (float), which is the sum of squared distances to the hubs.
    """
    total = 0.0
    for lbl, hub in zip(cluster_labels, hubs):
        mask = (labels == lbl)
        total += np.sum((data[mask] - hub)**2)
    return float(total)

def find_cluster_hub_nodes(data, labels, cluster_labels):
    """
    @brief Finds the hub nodes for each cluster.

    This function computes the hubs for each cluster by selecting the data points closest to the centroid 
    of each cluster. The hub is defined as the point closest to the cluster's centroid.

    @param data: The data points (numpy array).
    @param labels: The labels of each data point indicating the assigned cluster.
    @param cluster_labels: The unique cluster labels for the clustering result.
    @return: A tuple containing two elements:
        - hubs: An array of hub points, one for each cluster.
        - hub_indices: A list of indices of the hub points.
    """
    hubs = []
    hub_indices = []
    for lbl in cluster_labels:
        mask = (labels == lbl)
        subset = data[mask]
        centroid = subset.mean(axis=0)
        indices = np.where(mask)[0]
        dists = np.linalg.norm(data[indices] - centroid, axis=1)
        i_min = np.argmin(dists)
        hub_idx = indices[i_min]
        hubs.append(data[hub_idx])
        hub_indices.append(int(hub_idx))
    return np.array(hubs), hub_indices

def plot_solution(sol, canvas):
    """
    @brief Plots the clustering solution and the hubs.

    This function plots the data points and assigns different colors to points based on their cluster labels.
    It also marks the hubs with red 'x' markers.

    @param sol: The `Solution` object that contains the clustering results.
    @param canvas: The matplotlib canvas on which the plot will be drawn.
    """
    df = sol.data
    fig = canvas.figure
    fig.clf()
    ax = fig.add_subplot(111)

    # Extract x, y arrays
    x = df.iloc[:, 0].to_numpy()
    y = df.iloc[:, 1].to_numpy()

    if not hasattr(sol, 'labels') or sol.labels is None:
        ax.scatter(x, y, color='black', label='Data')
    else:
        labels = sol.labels
        hubs = getattr(sol, 'hubs', None)
        for lbl in np.unique(labels):
            mask = labels == lbl
            ax.scatter(x[mask], y[mask], label=f"C{lbl}", alpha=0.7)
            for i in np.where(mask)[0]:
                ax.text(x[i], y[i], str(i), fontsize=8, alpha=0.6)
        if hubs is not None and len(hubs):
            ax.scatter(hubs[:, 0], hubs[:, 1], marker='x', s=100, c='red', label='Hubs')

    #ax.set_title("Clustering Solution")
    ax.set_xlabel(df.columns[0])
    ax.set_ylabel(df.columns[1])
    ax.legend(loc='best')

    # Manual axis limits with padding
    x_min, x_max = x.min(), x.max()
    y_min, y_max = y.min(), y.max()
    x_pad = (x_max - x_min) * 0.05 if x_max > x_min else 1.0
    y_pad = (y_max - y_min) * 0.05 if y_max > y_min else 1.0
    ax.set_xlim(x_min - x_pad, x_max + x_pad)
    ax.set_ylim(y_min - y_pad, y_max + y_pad)

    canvas.draw()

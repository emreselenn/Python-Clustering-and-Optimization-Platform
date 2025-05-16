import random
import numpy as np
from models.solution import Solution
from utils import calculate_objective

class HeuristicService:
    """
    @class HeuristicService
    @brief Provides heuristic methods for solution improvement.

    The `HeuristicService` class includes methods for heuristic optimization algorithms such as Hill Climbing
    and Simulated Annealing. These methods improve the provided solution by exploring neighbors and selecting
    the best one according to the objective function.
    """
    
    def __init__(self):
        """
        @brief Initializes the HeuristicService object.

        The constructor does not require parameters and initializes the `HeuristicService` instance.
        """
        pass

    def hill_climbing(self, init_sol: Solution, iterations: int = 1000) -> Solution:
        """
        @brief Performs Hill Climbing optimization on the initial solution.

        This method iteratively improves the solution by selecting random neighbors and accepting those with a 
        better objective value. It runs for a fixed number of iterations.

        @param init_sol: The initial `Solution` object to be optimized.
        @param iterations: The number of iterations to perform (default is 1000).
        @return: The best solution found after the specified number of iterations.
        """
        best = init_sol.copy()
        for _ in range(iterations):
            neighbor = self._random_neighbor(best)
            if neighbor.objective < best.objective:
                best = neighbor
        return best

    def simulated_annealing(self, init_sol: Solution,
                             iterations: int = 1000,
                             initial_temp: float = 100.0,
                             cooling_rate: float = 0.99) -> Solution:
        """
        @brief Performs Simulated Annealing optimization on the initial solution.

        This method attempts to improve the solution by selecting random neighbors and accepting those that improve
        the objective function. In addition, it probabilistically accepts worse solutions with a certain probability
        that decreases with temperature. The algorithm runs for a fixed number of iterations.

        @param init_sol: The initial `Solution` object to be optimized.
        @param iterations: The number of iterations to perform (default is 1000).
        @param initial_temp: The initial temperature for the annealing process (default is 100.0).
        @param cooling_rate: The rate at which the temperature cools down (default is 0.99).
        @return: The best solution found after the specified number of iterations.
        """
        current = init_sol.copy()
        best = init_sol.copy()
        temp = initial_temp
        for _ in range(iterations):
            neighbor = self._random_neighbor(current)
            delta = neighbor.objective - current.objective
            if delta < 0 or random.random() < np.exp(-delta / temp):
                current = neighbor
                if current.objective < best.objective:
                    best = current
            temp *= cooling_rate
        return best

    def _random_neighbor(self, sol: Solution) -> Solution:
        """
        @brief Selects a random neighbor solution.

        This method randomly selects a neighboring solution by applying one of the predefined neighbor 
        generation operations (relocate hub, reallocate node, or swap nodes).

        @param sol: The current `Solution` object to generate a neighbor from.
        @return: A randomly selected neighbor solution.
        """
        ops = [self._relocate_hub, self._reallocate_node, self._swap_nodes]
        return random.choice(ops)(sol)

    def _relocate_hub(self, sol: Solution) -> Solution:
        """
        @brief Relocates a hub to a random position.

        This method selects a random hub and replaces it with a randomly chosen data point. It then updates
        the solution's labels and computes the new objective value.

        @param sol: The current `Solution` object to modify.
        @return: The new `Solution` object after relocating the hub.
        """
        neighbor = sol.copy()
        labels = neighbor.labels.copy()
        cluster_labels = neighbor.cluster_labels
        hubs = neighbor.hubs.copy()
        # Select a random hub index and a random point to become new hub
        hub_idx = random.choice(range(len(hubs)))
        point_idx = random.choice(range(len(neighbor.data)))
        hubs[hub_idx] = neighbor.data.values[point_idx]
        # Reassign labels
        dist = np.linalg.norm(neighbor.data.values[:, None, :] - hubs[None, :, :], axis=2)
        labels = np.argmin(dist, axis=1)
        neighbor.set_result(labels, cluster_labels, hubs,
                            calculate_objective(neighbor.data.values, labels, hubs, cluster_labels))
        return neighbor

    def _reallocate_node(self, sol: Solution) -> Solution:
        """
        @brief Moves a random node to a different cluster.

        This method selects a random node and moves it to another cluster. It then recomputes the hub positions
        and updates the solution's labels and objective value.

        @param sol: The current `Solution` object to modify.
        @return: The new `Solution` object after reallocating the node.
        """
        neighbor = sol.copy()
        labels = neighbor.labels.copy()
        cluster_labels = neighbor.cluster_labels
        hubs = neighbor.hubs.copy()
        # Move one random node to a different cluster
        node_idx = random.choice(range(len(labels)))
        current_cluster = labels[node_idx]
        other_clusters = [c for c in cluster_labels if c != current_cluster]
        if not other_clusters:
            return neighbor
        labels[node_idx] = random.choice(other_clusters)
        # Recompute hubs as mean of assigned points
        for i, cl in enumerate(cluster_labels):
            points = neighbor.data.values[labels == cl]
            if len(points) > 0:
                hubs[i] = np.mean(points, axis=0)
        neighbor.set_result(labels, cluster_labels, hubs,
                            calculate_objective(neighbor.data.values, labels, hubs, cluster_labels))
        return neighbor

    def _swap_nodes(self, sol: Solution) -> Solution:
        """
        @brief Swaps the clusters of two random nodes.

        This method randomly selects two nodes and swaps their clusters. It then recomputes the hub positions
        and updates the solution's labels and objective value.

        @param sol: The current `Solution` object to modify.
        @return: The new `Solution` object after swapping the nodes.
        """
        neighbor = sol.copy()
        labels = neighbor.labels.copy()
        cluster_labels = neighbor.cluster_labels
        hubs = neighbor.hubs.copy()
        # Swap clusters of two random nodes
        i, j = random.sample(range(len(labels)), 2)
        labels[i], labels[j] = labels[j], labels[i]
        # Recompute hubs
        for idx, cl in enumerate(cluster_labels):
            points = neighbor.data.values[labels == cl]
            if len(points) > 0:
                hubs[idx] = np.mean(points, axis=0)
        neighbor.set_result(labels, cluster_labels, hubs,
                            calculate_objective(neighbor.data.values, labels, hubs, cluster_labels))
        return neighbor

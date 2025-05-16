# controllers/clustering_controller.py

import numpy as np
from PyQt5.QtWidgets import (
    QMessageBox, QDialog, QFormLayout, QSpinBox,
    QComboBox, QLineEdit, QPushButton
)
from .commands import SetInitialSolutionCommand
from utils import calculate_objective, find_cluster_hub_nodes

class KMeansParamDialog(QDialog):
    """
    @brief A dialog for setting K-Means clustering parameters.

    This dialog allows users to set parameters for the K-Means clustering algorithm,
    such as the number of clusters, initialization method, maximum iterations, and algorithm.
    """

    def __init__(self, parent=None):
        """
        @brief Initializes the KMeansParamDialog.

        This method sets up the dialog with widgets for configuring the K-Means algorithm parameters.

        @param parent: The parent widget for this dialog, typically the main window.
        """
        super().__init__(parent)
        self.setWindowTitle("K-Means Parameters")
        form = QFormLayout(self)

        # Number of clusters input
        self.spin_n = QSpinBox()
        self.spin_n.setRange(1, 1000)
        self.spin_n.setValue(8)
        form.addRow("n_clusters:", self.spin_n)

        # Initialization method dropdown
        self.combo_init = QComboBox()
        self.combo_init.addItems(["k-means++", "random"])
        form.addRow("init:", self.combo_init)

        # Maximum iterations input
        self.edit_max = QLineEdit("300")
        form.addRow("max_iter:", self.edit_max)

        # Algorithm selection dropdown
        self.combo_algo = QComboBox()
        self.combo_algo.addItems(["lloyd", "elkan"])
        form.addRow("algorithm:", self.combo_algo)

        # OK button to confirm settings
        btn = QPushButton("OK")
        btn.clicked.connect(self.accept)
        form.addRow(btn)

    def get_params(self):
        """
        @brief Retrieves the parameters set in the dialog.

        @return: A dictionary containing the parameters for the K-Means algorithm.
        """
        return {
            "n_clusters": self.spin_n.value(),
            "init": self.combo_init.currentText(),
            "max_iter": int(self.edit_max.text()),
            "algorithm": self.combo_algo.currentText()
        }


class ClusteringController:
    """
    @brief Controls the clustering process and user interface interactions.

    This class is responsible for managing the clustering operations, handling user inputs,
    and coordinating with the UI to apply clustering algorithms like K-Means, DBSCAN, etc.
    """

    def __init__(self, ui, service, app, cmd_mgr):
        """
        @brief Initializes the ClusteringController.

        This method sets up the controller with necessary services, the application,
        and command manager. It also connects UI elements to clustering methods.

        @param ui: The user interface object containing UI elements like buttons and menus.
        @param service: The service object that handles the clustering algorithms.
        @param app: The application instance containing main application logic.
        @param cmd_mgr: The command manager to execute and manage commands.
        """
        self.ui = ui
        self.svc = service
        self.app = app
        self.cmd = cmd_mgr

        # Initially disable heuristic menus
        ui.actionHillClimbing.setEnabled(False)
        ui.actionSimulatedAnnealing.setEnabled(False)

        # Connect menu items to respective clustering methods
        ui.actionKMeans.triggered.connect(lambda: self._cluster_with_params('kmeans'))
        for act, method in [
            (ui.actionAffinity, 'affinity'),
            (ui.actionMeanShift, 'meanshift'),
            (ui.actionSpectral, 'spectral'),
            (ui.actionHierarchical, 'hierarchical'),
            (ui.actionDBSCAN, 'dbscan'),
        ]:
            act.triggered.connect(lambda _, m=method: self.cluster(m))

    def _cluster_with_params(self, method):
        """
        @brief Prompts the user to input parameters for K-Means clustering.

        This method opens a dialog for the user to set the parameters for the K-Means algorithm.
        Once the parameters are set, it proceeds to call the `cluster` method with the chosen parameters.

        @param method: The clustering method to use, e.g., 'kmeans'.
        """
        dlg = KMeansParamDialog(self.app.main_window)
        if dlg.exec_():
            params = dlg.get_params()
            self.cluster('kmeans', **params)

    def cluster(self, method, **params):
        """
        @brief Executes the clustering algorithm and handles the results.

        This method runs the selected clustering algorithm with the provided parameters,
        processes the results, and updates the UI accordingly.

        @param method: The clustering algorithm method to apply (e.g., 'kmeans').
        @param params: The parameters for the clustering algorithm (e.g., n_clusters, init, etc.).
        """
        # 1) Check if data is loaded
        if not self.app.initial_solution:
            QMessageBox.warning(self.app.main_window, "Error", "Önce veri yükleyin.")
            return

        df = self.app.initial_solution.data

        # 2) Run the model and catch errors
        try:
            sol = self.svc.cluster(method, df, **params)
        except ValueError as e:
            msg = str(e)
            QMessageBox.critical(self.app.main_window, "Clustering Error", msg)
            self.ui.txtInfoPanel.clear()
            self.ui.txtInfoPanel.append(f"Error: {msg}")
            return
        except Exception as e:
            msg = f"Beklenmeyen hata: {e}"
            QMessageBox.critical(self.app.main_window, "Clustering Error", msg)
            self.ui.txtInfoPanel.clear()
            self.ui.txtInfoPanel.append(msg)
            return

        # 3) Calculate hubs and objective
        hubs, hub_idxs = find_cluster_hub_nodes(df.values, sol.labels, sol.cluster_labels)
        sol.hubs = hubs
        sol.hub_indices = hub_idxs
        sol.objective = calculate_objective(df.values, sol.labels, hubs, sol.cluster_labels)

        # 4) Apply the solution
        self.cmd.do(SetInitialSolutionCommand(self.app, sol))

        # 5) Update Info & Results panels
        self.ui.txtInfoPanel.clear()
        self.ui.txtInfoPanel.append(f"Clustering: {method.capitalize()}")
        self.ui.txtInfoPanel.append(f"Clusters: {len(sol.cluster_labels)}")
        self.ui.txtInfoPanel.append(f"Hubs: {hub_idxs}")

        rez = ""
        for lbl in sol.cluster_labels:
            ids = np.where(sol.labels == lbl)[0].tolist()
            rez += f"Cluster {lbl}: {ids}\n"
        self.ui.txtResults.setPlainText(rez)

        # 6) Enable/Disable heuristic menus based on hubs
        if len(sol.hubs) == 0:
            QMessageBox.information(
                self.app.main_window,
                "No Hubs",
                "Geçerli hub bulunamadı; heuristic devredışı kalacak."
            )
            self.ui.actionHillClimbing.setEnabled(False)
            self.ui.actionSimulatedAnnealing.setEnabled(False)
        else:
            self.ui.actionHillClimbing.setEnabled(True)
            self.ui.actionSimulatedAnnealing.setEnabled(True)

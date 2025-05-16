# controllers/file_controller.py

import os
import re
import numpy as np
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QInputDialog
from .commands import LoadDataCommand, ClearInitialCommand, SetInitialSolutionCommand
from utils import plot_solution, calculate_objective
from models.solution import Solution

class FileController:
    """
    @brief Manages file operations for loading, saving, exporting, and clearing data.

    This class handles the operations related to opening data files, saving and exporting the 
    initial solution, clearing the initial solution, and undo/redo functionality. It also 
    manages enabling and disabling UI elements based on the state of the application.
    """
    
    def __init__(self, ui, loader, app, cmd_mgr):
        """
        @brief Initializes the FileController.

        Sets up connections between the UI and the file-related operations, including loading,
        saving, exporting, and clearing data. Also manages the undo/redo functionality.

        @param ui: The user interface object for connecting UI elements.
        @param loader: The loader responsible for loading data from files.
        @param app: The application instance containing the solution data.
        @param cmd_mgr: The command manager used for handling commands.
        """
        self.ui = ui
        self.loader = loader
        self.app = app
        self.cmd = cmd_mgr

        # Exit actions
        ui.actionExit.triggered.connect(app.main_window.close)
        ui.btnExit.clicked.connect(app.main_window.close)

        # Open Data actions
        ui.actionOpenData.triggered.connect(self.open_data)
        ui.btnOpenData.clicked.connect(self.open_data)

        # Disable initial controls at the start
        for name in (
            'btnSaveInitial','actionSaveInitial',
            'btnExportInitial','actionExportInitial',
            'btnClearInitial','actionClearInitial',
            'btnUndoInitial','actionUndoInitial',
            'btnRedoInitial','actionRedoInitial'
        ):
            getattr(ui, name).setEnabled(False)
        ui.btnRunManual.setEnabled(False)

        # Disable clustering and heuristic until data is loaded
        for act in ui.menuClustering.actions(): act.setEnabled(False)
        for act in ui.menuHeuristic.actions(): act.setEnabled(False)

        # Bind initial handlers for saving, exporting, clearing, undo, and redo
        ui.btnSaveInitial.clicked.connect(self.save_initial)
        ui.actionSaveInitial.triggered.connect(self.save_initial)
        ui.btnExportInitial.clicked.connect(self.export_initial)
        ui.actionExportInitial.triggered.connect(self.export_initial)
        ui.btnClearInitial.clicked.connect(self.clear_initial)
        ui.actionClearInitial.triggered.connect(self.clear_initial)
        ui.btnUndoInitial.clicked.connect(self.on_undo)
        ui.actionUndoInitial.triggered.connect(self.on_undo)
        ui.btnRedoInitial.clicked.connect(self.on_redo)
        ui.actionRedoInitial.triggered.connect(self.on_redo)

        # Manual Solution action
        ui.btnRunManual.clicked.connect(self.run_manual)

    def open_data(self):
        """
        @brief Opens the data file and loads it into the application.

        This method allows the user to select a file, loads its data into the application,
        and enables the necessary UI controls after the data has been successfully loaded.
        """
        path, _ = QFileDialog.getOpenFileName(
            self.app.main_window, "Open Data", "", "Text Files (*.txt)"
        )
        if not path:
            return
        self.cmd.do(LoadDataCommand(self.app, self.loader, path))
        # Enable initial controls and clustering menu
        self.update_controls()

    def save_initial(self):
        """
        @brief Saves the initial solution to a file.

        This method prompts the user to choose a location to save the initial solution as a text file.
        """
        sol = self.app.initial_solution
        if not sol:
            return
        p, _ = QFileDialog.getSaveFileName(
            self.app.main_window, "Save Initial As...", "", "Text Files (*.txt)"
        )
        if p:
            sol.data.to_csv(p, sep='\t', header=False, index=False)

    def export_initial(self):
        """
        @brief Exports the initial solution to a specified file.

        This method allows the user to export the initial solution to various formats,
        including text, JPEG, and PNG. The appropriate action is taken based on the file extension.
        """
        p, _ = QFileDialog.getSaveFileName(
            self.app.main_window,
            "Export Initial As...", "",
            "Text Files (*.txt);;JPEG (*.jpg);;PNG (*.png)"
        )
        if not p:
            return
        ext = os.path.splitext(p)[1].lower()
        if ext == '.txt':
            self.app.initial_solution.data.to_csv(p, sep='\t', header=False, index=False)
        else:
            self.app.canvasInitial.figure.savefig(p)

    def clear_initial(self):
        """
        @brief Clears the initial solution.

        This method clears the initial solution and updates the UI accordingly.
        """
        self.cmd.do(ClearInitialCommand(self.app))
        self.update_controls()

    def on_undo(self):
        """
        @brief Undoes the last action in the edit history.

        This method reverts the last executed command by invoking the undo method from the command manager.
        """
        self.cmd.undo()
        self.update_controls()

    def on_redo(self):
        """
        @brief Redoes the last undone action in the edit history.

        This method re-applies the last undone command by invoking the redo method from the command manager.
        """
        self.cmd.redo()
        self.update_controls()

    def update_controls(self):
        """
        @brief Updates the enabled state of UI controls based on the current state of the application.

        This method enables or disables the relevant buttons and menu items based on whether the initial solution 
        is loaded, and the current undo/redo state.
        """
        has = self.app.initial_solution is not None
        # Enable/disable initial panel controls
        for name in (
            'btnSaveInitial','actionSaveInitial',
            'btnExportInitial','actionExportInitial',
            'btnClearInitial','actionClearInitial'
        ):
            getattr(self.ui, name).setEnabled(has)
        # Enable/disable clustering menu items
        for act in self.ui.menuClustering.actions():
            act.setEnabled(has)
        # Reset heuristic menu
        for act in self.ui.menuHeuristic.actions():
            act.setEnabled(False)
        # Enable/disable undo/redo buttons
        can_u = self.cmd.pointer >= 0
        can_r = self.cmd.pointer + 1 < len(self.cmd.history)
        self.ui.btnUndoInitial.setEnabled(can_u)
        self.ui.actionUndoInitial.setEnabled(can_u)
        self.ui.btnRedoInitial.setEnabled(can_r)
        self.ui.actionRedoInitial.setEnabled(can_r)
        # Enable/disable manual run button
        self.ui.btnRunManual.setEnabled(has)

    def run_manual(self):
        """
        @brief Runs the manual clustering process.

        This method allows the user to manually assign hubs and nodes to clusters. The solution is then calculated
        and displayed on the UI with the corresponding objective value and clustering results.
        """
        sol0 = self.app.initial_solution
        if sol0 is None:
            QMessageBox.warning(self.app.main_window, "Error", "No initial solution to run manual on.")
            return
        data = sol0.data.values
        # Get hubs input from the user
        hubs_txt = self.ui.leHubs.toPlainText()
        try:
            hubs_idx = [int(x) for x in re.split(r'[\s,;]+', hubs_txt) if x.strip()]
        except ValueError:
            QMessageBox.warning(self.app.main_window, "Error", "Invalid hubs list format.")
            return
        if not hubs_idx or min(hubs_idx) < 0 or max(hubs_idx) >= data.shape[0]:
            QMessageBox.warning(self.app.main_window, "Error", "Hub indices out of range.")
            return
        # Get manual node assignments from the user
        nodes_txt = self.ui.leNodes.toPlainText().strip()
        manual_assign = {}
        if nodes_txt:
            try:
                for part in re.split(r'[\s,;]+', nodes_txt):
                    i, j = part.split(':')
                    manual_assign[int(i)] = int(j)
            except Exception:
                QMessageBox.warning(self.app.main_window, "Error", "Invalid nodes assignment format.")
                return
        # Perform clustering by hubs
        hubs = data[hubs_idx]
        labels = np.argmin(np.linalg.norm(data[:, None, :] - hubs[None, :, :], axis=2), axis=1)
        # Override manual assignments
        for node_i, cl_i in manual_assign.items():
            if 0 <= node_i < data.shape[0] and 0 <= cl_i < len(hubs_idx):
                labels[node_i] = cl_i
        cluster_labels = list(range(len(hubs_idx)))
        # Calculate objective value
        obj = calculate_objective(data, labels, hubs, cluster_labels)
        # Create and set the solution
        sol = Solution(data=sol0.data)
        sol.labels = labels
        sol.cluster_labels = cluster_labels
        sol.hubs = hubs
        sol.hub_indices = hubs_idx
        sol.objective = obj
        self.cmd.do(SetInitialSolutionCommand(self.app, sol))
        # Plot the solution
        plot_solution(sol, self.app.canvasInitial)
        # Update the info panel
        self.ui.txtInfoPanel.clear()
        self.ui.txtInfoPanel.append("Manual Solution")
        self.ui.txtInfoPanel.append(f"Hubs: {hubs_idx}")
        if manual_assign:
            self.ui.txtInfoPanel.append(f"Manual nodes: {manual_assign}")
        self.ui.txtInfoPanel.append(f"Clusters: {len(cluster_labels)}")
        self.ui.txtInfoPanel.append(f"Objective: {obj:.3f}")
        # Update the results panel
        rez = ""
        for lbl in cluster_labels:
            idxs = np.where(labels == lbl)[0].tolist()
            rez += f"Cluster {lbl}: {idxs}\n"
        self.ui.txtResults.setPlainText(rez)
        # Enable heuristic menu
        for act in self.ui.menuHeuristic.actions():
            act.setEnabled(True)
        # Update initial controls
        self.update_controls()

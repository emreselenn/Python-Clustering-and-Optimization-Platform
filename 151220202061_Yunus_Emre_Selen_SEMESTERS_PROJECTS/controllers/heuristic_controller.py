# controllers/heuristic_controller.py

import os
import numpy as np
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from .commands import SetFinalSolutionCommand

class HeuristicController:
    """
    @brief Manages the heuristic operations (Hill Climbing and Simulated Annealing).

    The `HeuristicController` class handles the execution of heuristic methods such as Hill Climbing and Simulated Annealing.
    It also manages the UI updates and final solution handling (save, export, undo, redo).
    """
    
    def __init__(self, ui, service, app, cmd_mgr):
        """
        @brief Initializes the HeuristicController.

        This method connects UI actions (buttons and menu items) to their respective functions and initializes 
        the controller with necessary services, application reference, and command manager.

        @param ui: The user interface object containing UI elements like buttons and actions.
        @param service: The service object that handles the heuristic algorithms.
        @param app: The application instance, which contains the data and manages the solution.
        @param cmd_mgr: The command manager used for executing and managing commands.
        """
        self.ui = ui
        self.svc = service
        self.app = app
        self.cmd = cmd_mgr

        # Initially disable heuristic menus
        self.ui.actionHillClimbing.setEnabled(False)
        self.ui.actionSimulatedAnnealing.setEnabled(False)

        # Connect menu actions to respective functions
        self.ui.actionHillClimbing.triggered.connect(lambda: self.run('hill'))
        self.ui.actionSimulatedAnnealing.triggered.connect(lambda: self.run('annealing'))

        # Bind final panel buttons to their functions
        for btn_name, act_name, fn in [
            ('btnSaveFinal', 'actionSaveFinal', self.save),
            ('btnExportFinal', 'actionExportFinal', self.export),
            ('btnClearFinal', 'actionClearFinal', self.clear),
            ('btnUndoFinal', 'actionUndoFinal', self.undo),
            ('btnRedoFinal', 'actionRedoFinal', self.redo),
        ]:
            getattr(self.ui, btn_name).clicked.connect(fn)
            getattr(self.ui, act_name).triggered.connect(fn)

        # Initially, disable final panel controls
        self.update_final_controls()

    def run(self, method):
        """
        @brief Runs the selected heuristic method (Hill Climbing or Simulated Annealing).

        This method applies the selected heuristic method to the current solution, performs the optimization,
        and updates the final solution and UI.

        @param method: The heuristic method to be used, either 'hill' for Hill Climbing or 'annealing' for Simulated Annealing.
        """
        base = self.app.initial_solution
        # Check if a valid clustering exists
        if base is None or not hasattr(base, 'labels') or not hasattr(base, 'hubs') or len(base.hubs) == 0:
            QMessageBox.warning(self.app.main_window, "Error",
                                "Heuristic cannot be applied: No valid clustering result available.")
            return

        # Run the heuristic method
        try:
            sol = (self.svc.hill_climbing(base) if method == 'hill'
                   else self.svc.simulated_annealing(base))
        except Exception as e:
            msg = str(e)
            QMessageBox.critical(self.app.main_window, "Heuristic Error", msg)
            self.ui.txtInfoPanel.clear()
            self.ui.txtInfoPanel.append(f"Error: {msg}")
            return

        # Apply the final solution
        self.cmd.do(SetFinalSolutionCommand(self.app, sol))

        # Update information panels
        title = "Hill Climbing" if method == 'hill' else "Simulated Annealing"
        self.ui.txtInfoPanel.clear()
        self.ui.txtInfoPanel.append(f"Heuristic: {title}")
        self.ui.txtInfoPanel.append(f"Clusters: {len(sol.cluster_labels)}")
        rez = ""
        for lbl in sol.cluster_labels:
            idxs = np.where(sol.labels == lbl)[0].tolist()
            rez += f"Cluster {lbl}: {idxs}\n"
        self.ui.txtResults.setPlainText(rez)

        # Update final controls
        self.update_final_controls()

    def save(self):
        """
        @brief Saves the final solution to a file.

        This method allows the user to save the final solution to a file (as a text file).
        """
        sol = self.app.final_solution
        if sol:
            path, _ = QFileDialog.getSaveFileName(
                self.app.main_window, "Save Final As...", "", "Text Files (*.txt)")
            if path:
                sol.data.to_csv(path, sep='\t', header=False, index=False)

    def export(self):
        """
        @brief Exports the final solution to a specified file.

        This method allows the user to export the final solution in various formats including text, JPEG, and PNG.
        The appropriate action is taken based on the selected file extension.
        """
        sol = self.app.final_solution
        if sol:
            path, _ = QFileDialog.getSaveFileName(
                self.app.main_window, "Export Final As...", "",
                "Text Files (*.txt);;JPEG (*.jpg);;PNG (*.png)"
            )
            if path:
                ext = os.path.splitext(path)[1].lower()
                if ext == '.txt':
                    sol.data.to_csv(path, sep='\t', header=False, index=False)
                else:
                    self.app.canvasFinal.figure.savefig(path)

    def clear(self):
        """
        @brief Clears the final solution.

        This method clears the current final solution and updates the UI.
        """
        self.cmd.do(SetFinalSolutionCommand(self.app, None))
        self.update_final_controls()

    def undo(self):
        """
        @brief Undoes the last action in the final solution history.

        This method undoes the last change made to the final solution and updates the UI.
        """
        self.cmd.undo()
        self.update_final_controls()

    def redo(self):
        """
        @brief Redoes the last undone action in the final solution history.

        This method re-applies the last undone change to the final solution and updates the UI.
        """
        self.cmd.redo()
        self.update_final_controls()

    def update_final_controls(self):
        """
        @brief Updates the enabled state of final solution controls.

        This method enables or disables the UI controls related to the final solution based on whether a valid
        final solution exists. It also updates the undo/redo buttons based on the command history.
        """
        has = self.app.final_solution is not None and hasattr(self.app.final_solution, 'labels')
        # Enable/disable save/export/clear controls only when a final solution exists
        for name in ('btnSaveFinal', 'actionSaveFinal',
                     'btnExportFinal', 'actionExportFinal',
                     'btnClearFinal', 'actionClearFinal'):
            getattr(self.ui, name).setEnabled(has)
        # Enable/disable undo/redo buttons based on the command history
        can_undo = self.cmd.pointer >= 0
        can_redo = self.cmd.pointer + 1 < len(self.cmd.history)
        self.ui.btnUndoFinal.setEnabled(can_undo)
        self.ui.actionUndoFinal.setEnabled(can_undo)
        self.ui.btnRedoFinal.setEnabled(can_redo)
        self.ui.actionRedoFinal.setEnabled(can_redo)

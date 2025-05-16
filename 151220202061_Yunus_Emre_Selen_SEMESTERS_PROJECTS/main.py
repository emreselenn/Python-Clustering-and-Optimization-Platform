# File: main.py
# nimnim

import sys
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from qt_design import Ui_MainWindow
from models.data_loader import DataLoader
from services.clustering_service import ClusteringService
from services.heuristic_service import HeuristicService
from undo_redo import CommandManager
from controllers import (
    FileController,
    EditController,
    ClusteringController,
    HeuristicController
)

class Application:
    """
    @class Application
    @brief Manages the overall application flow and user interface.

    The `Application` class sets up the PyQt5 application, the main window, the required models and services, 
    and initializes the controllers for file management, editing, clustering, and heuristic operations. It also 
    embeds the Matplotlib canvases for plotting data.
    """

    def __init__(self):
        """
        @brief Initializes the application, the main window, and all required services and controllers.

        This constructor sets up the PyQt5 main window, the models (such as the data loader, clustering service, and heuristic service), 
        the command managers (for managing the history of operations), and the controllers for file handling, editing, clustering, 
        and heuristics. Additionally, it prepares the Matplotlib canvases for displaying clustering results.
        """
        # Qt application and main window
        self.app = QtWidgets.QApplication(sys.argv)
        self.main_window = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.main_window)

        # Models & services
        self.data_loader = DataLoader()
        self.clustering_service = ClusteringService()
        self.heuristic_service = HeuristicService()

        # Command managers: one for initial, one for final
        self.initial_cmd_mgr = CommandManager()
        self.final_cmd_mgr   = CommandManager()

        # Solution placeholders
        self.initial_solution = None
        self.final_solution   = None

        # Embed matplotlib canvases
        fig1 = plt.figure()
        self.canvasInitial = FigureCanvas(fig1)
        lay1 = QVBoxLayout(self.ui.plotInitial)
        lay1.setContentsMargins(0, 0, 0, 0)
        lay1.addWidget(self.canvasInitial)

        fig2 = plt.figure()
        self.canvasFinal = FigureCanvas(fig2)
        lay2 = QVBoxLayout(self.ui.plotFinal)
        lay2.setContentsMargins(0, 0, 0, 0)
        lay2.addWidget(self.canvasFinal)

        # Controllers
        self.file_controller = FileController(
            self.ui, self.data_loader, self, self.initial_cmd_mgr
        )
        self.edit_controller = EditController(
            self.ui, self, self.initial_cmd_mgr, self.final_cmd_mgr
        )
        self.clustering_controller = ClusteringController(
            self.ui, self.clustering_service, self, self.initial_cmd_mgr
        )
        self.heuristic_controller = HeuristicController(
            self.ui, self.heuristic_service, self, self.final_cmd_mgr
        )

    def run(self):
        """
        @brief Starts the PyQt5 application and displays the main window.

        This method starts the PyQt5 event loop and shows the main application window. It waits for user interactions 
        and handles application events until the user closes the window.
        """
        self.main_window.show()
        sys.exit(self.app.exec_())


if __name__ == '__main__':
    """
    @brief Main entry point of the application.

    This block runs the `Application` class, starting the PyQt5 application and displaying the main window.
    """
    Application().run()

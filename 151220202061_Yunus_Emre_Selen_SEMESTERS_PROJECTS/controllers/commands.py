# controllers/commands.py

from undo_redo import Command
from utils import plot_solution

class LoadDataCommand(Command):
    """
    @brief Command to load data from a file and set it as the initial solution.

    This command loads data from a given file path, creates a new `Solution` object, 
    and sets it as the initial solution in the application. It also plots the solution.
    """
    
    def __init__(self, app, loader, path):
        """
        @brief Initializes the LoadDataCommand.

        @param app: The application object containing the initial solution.
        @param loader: The data loader that handles loading the data from the file.
        @param path: The file path from which the data should be loaded.
        """
        self.app = app
        self.loader = loader
        self.path = path
        self.prev = app.initial_solution
        self.new = None

    def execute(self):
        """
        @brief Executes the data loading and sets the initial solution.

        Loads the data from the specified file and creates a new `Solution` object.
        Sets this new solution as the initial solution and plots it on the initial canvas.
        """
        df = self.loader.load_txt(self.path)
        from models.solution import Solution
        self.new = Solution(data=df)
        self.app.initial_solution = self.new
        plot_solution(self.new, self.app.canvasInitial)
        self.app.canvasInitial.draw()

    def undo(self):
        """
        @brief Undoes the data loading operation.

        Reverts the application to the previous initial solution and re-renders the solution.
        If there is no previous solution, it clears the canvas.
        """
        self.app.initial_solution = self.prev
        if self.prev:
            plot_solution(self.prev, self.app.canvasInitial)
        else:
            self.app.canvasInitial.figure.clear()
        self.app.canvasInitial.draw()

    def redo(self):
        """
        @brief Redoes the data loading operation.

        Re-executes the `execute()` method to load the data and set the initial solution.
        """
        self.execute()


class ClearInitialCommand(Command):
    """
    @brief Command to clear the initial solution.

    This command clears the initial solution in the application and updates the canvas.
    """
    
    def __init__(self, app):
        """
        @brief Initializes the ClearInitialCommand.

        @param app: The application object containing the initial solution.
        """
        self.app = app
        self.prev = app.initial_solution

    def execute(self):
        """
        @brief Clears the initial solution and the initial canvas.

        This method clears the initial solution and clears the canvas used for displaying the solution.
        """
        self.app.initial_solution = None
        self.app.canvasInitial.figure.clear()
        self.app.canvasInitial.draw()

    def undo(self):
        """
        @brief Undoes the clear operation and restores the previous solution.

        This method restores the previous initial solution and re-renders it on the canvas.
        """
        if self.prev:
            self.app.initial_solution = self.prev
            plot_solution(self.prev, self.app.canvasInitial)
            self.app.canvasInitial.draw()

    def redo(self):
        """
        @brief Redoes the clear operation.

        Clears the initial solution again and clears the canvas.
        """
        self.execute()


class SetInitialSolutionCommand(Command):
    """
    @brief Command to set a new initial solution.

    This command sets the provided solution as the initial solution and updates the canvas.
    """
    
    def __init__(self, app, sol):
        """
        @brief Initializes the SetInitialSolutionCommand.

        @param app: The application object containing the initial solution.
        @param sol: The new solution to be set as the initial solution.
        """
        self.app = app
        self.new = sol
        self.prev = app.initial_solution

    def execute(self):
        """
        @brief Sets the new initial solution and updates the canvas.

        This method sets the new solution as the initial solution and plots it on the initial canvas.
        """
        self.app.initial_solution = self.new
        if self.new:
            plot_solution(self.new, self.app.canvasInitial)
        else:
            self.app.canvasInitial.figure.clear()
        self.app.canvasInitial.draw()

    def undo(self):
        """
        @brief Undoes the setting of the new initial solution.

        Reverts to the previous initial solution and re-renders it on the canvas.
        If there is no previous solution, it clears the canvas.
        """
        self.app.initial_solution = self.prev
        if self.prev:
            plot_solution(self.prev, self.app.canvasInitial)
        else:
            self.app.canvasInitial.figure.clear()
        self.app.canvasInitial.draw()

    def redo(self):
        """
        @brief Redoes the setting of the new initial solution.

        Re-executes the `execute()` method to set the new solution as the initial solution.
        """
        self.execute()


class SetFinalSolutionCommand(Command):
    """
    @brief Command to set a new final solution.

    This command sets the provided solution as the final solution and updates the canvas.
    """
    
    def __init__(self, app, sol):
        """
        @brief Initializes the SetFinalSolutionCommand.

        @param app: The application object containing the final solution.
        @param sol: The new solution to be set as the final solution.
        """
        self.app = app
        self.new = sol
        self.prev = app.final_solution

    def execute(self):
        """
        @brief Sets the new final solution and updates the canvas.

        This method sets the new solution as the final solution and plots it on the final canvas.
        """
        self.app.final_solution = self.new
        if self.new:
            plot_solution(self.new, self.app.canvasFinal)
        else:
            self.app.canvasFinal.figure.clear()
        self.app.canvasFinal.draw()

    def undo(self):
        """
        @brief Undoes the setting of the new final solution.

        Reverts to the previous final solution and re-renders it on the canvas.
        If there is no previous solution, it clears the canvas.
        """
        self.app.final_solution = self.prev
        if self.prev:
            plot_solution(self.prev, self.app.canvasFinal)
        else:
            self.app.canvasFinal.figure.clear()
        self.app.canvasFinal.draw()

    def redo(self):
        """
        @brief Redoes the setting of the new final solution.

        Re-executes the `execute()` method to set the new solution as the final solution.
        """
        self.execute()

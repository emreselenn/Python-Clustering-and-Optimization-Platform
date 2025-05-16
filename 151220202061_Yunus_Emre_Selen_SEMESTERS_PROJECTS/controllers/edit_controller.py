# controllers/edit_controller.py

from abc import ABC, abstractmethod

class Command(ABC):
    """
    @brief Abstract base class for all edit commands.

    This abstract class defines the interface for all edit operations that will be implemented
    by concrete command classes. Each command must implement the `execute` and `undo` methods.
    """
    
    @abstractmethod
    def execute(self):
        """
        @brief Executes the command.

        This method performs the operation associated with the command.
        """
        pass

    @abstractmethod
    def undo(self):
        """
        @brief Undoes the command.

        This method reverts the operation performed by `execute`.
        """
        pass

class EditController:
    """
    @brief Manages edit operations using the command pattern.

    The `EditController` class handles various edit operations (like clear, add point, delete point)
    using the command pattern and keeps track of the undo/redo history.
    """

    def __init__(self, ui, app_ref, init_mgr, final_mgr):
        """
        @brief Initializes the EditController.

        Sets up the edit controller with references to the UI, application, initial manager, and final manager.

        @param ui: The user interface object, which controls the UI elements like buttons.
        @param app_ref: A reference to the application.
        @param init_mgr: The initial manager for handling the initial data.
        @param final_mgr: The final manager for handling the final data.
        """
        self.ui = ui
        self.app = app_ref
        self.init_mgr = init_mgr
        self.final_mgr = final_mgr

        # Undo and redo stacks
        self._undo_stack = []
        self._redo_stack = []

    def execute(self, cmd: Command):
        """
        @brief Executes a new edit command and adds it to the undo stack.

        This method runs the given command and clears the redo stack. It also updates the UI buttons 
        to reflect the current undo/redo state.

        @param cmd: The command to be executed.
        """
        cmd.execute()
        self._undo_stack.append(cmd)
        self._redo_stack.clear()
        self._update_ui_buttons()

    def undo(self):
        """
        @brief Undoes the last executed command.

        This method pops the last command from the undo stack, undoes it, and adds it to the redo stack. 
        It also updates the UI buttons to reflect the new state.
        """
        if not self._undo_stack:
            return
        cmd = self._undo_stack.pop()
        cmd.undo()
        self._redo_stack.append(cmd)
        self._update_ui_buttons()

    def redo(self):
        """
        @brief Redoes the last undone command.

        This method pops the last command from the redo stack, re-executes it, and adds it to the undo stack.
        It also updates the UI buttons to reflect the new state.
        """
        if not self._redo_stack:
            return
        cmd = self._redo_stack.pop()
        cmd.execute()
        self._undo_stack.append(cmd)
        self._update_ui_buttons()

    def clear_history(self):
        """
        @brief Clears all undo and redo history.

        This method clears both the undo and redo stacks, effectively resetting the history.
        It also updates the UI buttons to reflect the cleared history.
        """
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._update_ui_buttons()

    def _update_ui_buttons(self):
        """
        @brief Updates the enabled state of the undo/redo buttons.

        This method updates the UI buttons for undo and redo based on the current state of the undo/redo stacks.
        Example: 
            self.ui.undoButton.setEnabled(bool(self._undo_stack))
            self.ui.redoButton.setEnabled(bool(self._redo_stack))
        """
        pass


# --- Example Commands ---

class ClearInitialCommand(Command):
    """
    @brief Command to clear the initial manager's data.

    This command clears the data in the initial manager and allows for undo/redo functionality.
    """
    
    def __init__(self, controller: EditController):
        """
        @brief Initializes the ClearInitialCommand.

        @param controller: The `EditController` object that will manage this command.
        """
        self.ctrl = controller
        self.prev_text = None

    def execute(self):
        """
        @brief Executes the clear command on the initial manager.

        This method stores the current text of the initial manager and then clears it.
        """
        self.prev_text = self.ctrl.init_mgr.get_text()
        self.ctrl.init_mgr.clear()

    def undo(self):
        """
        @brief Undoes the clear command and restores the initial manager's text.

        This method restores the initial manager's text to its previous state before it was cleared.
        """
        self.ctrl.init_mgr.set_text(self.prev_text)

class ClearFinalCommand(Command):
    """
    @brief Command to clear the final manager's data.

    This command clears the data in the final manager and allows for undo/redo functionality.
    """
    
    def __init__(self, controller: EditController):
        """
        @brief Initializes the ClearFinalCommand.

        @param controller: The `EditController` object that will manage this command.
        """
        self.ctrl = controller
        self.prev_text = None

    def execute(self):
        """
        @brief Executes the clear command on the final manager.

        This method stores the current text of the final manager and then clears it.
        """
        self.prev_text = self.ctrl.final_mgr.get_text()
        self.ctrl.final_mgr.clear()

    def undo(self):
        """
        @brief Undoes the clear command and restores the final manager's text.

        This method restores the final manager's text to its previous state before it was cleared.
        """
        self.ctrl.final_mgr.set_text(self.prev_text)

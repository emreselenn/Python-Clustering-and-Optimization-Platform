# File: undo_redo.py
# nimnim
"""
! @file undo_redo.py
! @brief Defines Command pattern for undo/redo functionality.
"""

class Command:
    """
    ! @class Command
    ! @brief Abstract base for undoable/redoable commands.

    This is an abstract class that defines the interface for all undoable and redoable commands. 
    Each specific command class must implement the `execute()` and `undo()` methods.
    """

    def execute(self):
        """
        ! @brief Executes the command.

        This method is intended to perform the action of the command. It should be implemented by 
        each subclass to define the specific action of the command.

        @throws NotImplementedError: If not implemented by the subclass.
        """
        raise NotImplementedError("Command execute() must be implemented.")

    def undo(self):
        """
        ! @brief Undoes the command.

        This method undoes the action performed by the `execute()` method. It should be implemented by 
        each subclass to define the specific undo action of the command.

        @throws NotImplementedError: If not implemented by the subclass.
        """
        raise NotImplementedError("Command undo() must be implemented.")


class CommandManager:
    """
    ! @class CommandManager
    ! @brief Manages undo/redo stacks of Command instances.

    The `CommandManager` class is responsible for managing a stack of commands and providing 
    undo/redo functionality. It maintains the history of commands and allows users to undo or redo actions.
    """

    def __init__(self):
        """
        ! @brief Initializes the CommandManager instance.

        The constructor initializes an empty history stack and sets the pointer to -1.
        """
        self.history = []  # type: list[Command]
        self.pointer = -1

    def do(self, command: Command):
        """
        ! @brief Execute a new command and record it.

        This method executes a new command and stores it in the history stack. The history is trimmed 
        to remove any redoable commands that follow the current pointer.

        @param command: The command to be executed.
        """
        command.execute()
        self.history = self.history[:self.pointer + 1]
        self.history.append(command)
        self.pointer += 1

    def undo(self):
        """
        ! @brief Undo the last command if available.

        This method undoes the last executed command and moves the pointer backward in the history stack. 
        If no command is available to undo, nothing happens.

        @throws IndexError: If no command is available to undo.
        """
        if self.pointer >= 0:
            cmd = self.history[self.pointer]
            cmd.undo()
            self.pointer -= 1

    def redo(self):
        """
        ! @brief Redo the next command if available.

        This method re-executes the next undone command and moves the pointer forward in the history stack.
        If no command is available to redo, nothing happens.

        @throws IndexError: If no command is available to redo.
        """
        if self.pointer + 1 < len(self.history):
            self.pointer += 1
            cmd = self.history[self.pointer]
            cmd.execute()

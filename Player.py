"""
Date: 19/09/2021
Author: Matteo Nunziante
Description: Four In A Line game
Example of reinforcement learning applied to a game:
    -> it's possible to train 2 players (one that start first and one that start for second)
    -> the training can be between the 2 artificial player and also during the game with a human player
"""

import pickle
from pathlib import Path
import numpy as np

from Enumerations import CellState


class Player:
    def __init__(self, name, symbol):
        """
        Initialize name and symbol of the player
        :param name: name of the player
        :param symbol: symbol of the player: 'X' if first player, 'O' otherwise
        """
        self.name = name
        self.symbol = symbol

    def setName(self , name):
        """
        Set the name of the player
        :param name: the name of the player
        :return: nothing
        """
        self.name = name

    def get_available_x(self, board, y):
        """
        Method that given a column return the first row available
        :param y: is the columns chosen
        :param board: current game board
        :return: the x coordinate
        """
        # Check all the position in the column selected starting from the base
        for x in range(board.shape[0]):
            if board[x, y] == CellState.empty_Value:
                # print("Chosen x: " , x)
                return x

    def addState(self, state):
        pass

    def feedReward(self, reward):
        pass

    def reset(self):
        pass


class ArtificialPlayer(Player):

    def __init__(self, name, symbol, exp_rate=0.4):
        """
        Initialize the artificial player
        :param name: name of the player
        :param symbol: symbol of the player
        :param exp_rate: constant indicating the probability of performing a random action
        """
        super().__init__(name, symbol)

        # To save all positions taken
        self.states = []
        # State -> value
        self.states_value = {}
        # Epsilon-greedy method to balance between exploration and exploitation
        self.exp_rate = exp_rate
        # learning rate
        self.lr = 0.8
        self.gamma = 0.9

    def getHash(self, board, board_rows=6, board_cols=7):
        """
        Get the hash of a board
        :param board: the board of whom calculate the hash
        :param board_rows: number of rows in the board
        :param board_cols: number of columns in the board
        :return: the hah of the board
        """
        boardHash = str(board.reshape(board_rows * board_cols))
        return boardHash

    def chooseAction(self, positions, board):
        """
        Method that chooses the action of the artificial player:
            - random action (40% of the actions during the training game , never otherwise)
            - action related to his experience
        :param positions: is a list containing all the positions in which is possible perform an action
        :param board: is the board of the game
        :return: a tuple containing the coordinates of the board on which do the action (add the symbol of the player)
        """
        # Check if with one action the player can win -> do it

        for y in positions:
            # Make a copy of the board
            next_board = board.copy()
            # Save the pair (x,y)
            position = (self.get_available_x(next_board, y), y)
            # Add the symbol in a possible position
            next_board[position] = self.symbol
            if self.action_check(next_board, self.symbol):
                # print("Return a position to win")
                return y

        if self.symbol == CellState.X_Value:
            enemy_symbol = CellState.O_Value
        else:
            enemy_symbol = CellState.X_Value

        # Check if with one action the enemy can win -> block him
        for y in positions:
            # Make a copy of the board
            next_board = board.copy()
            # Save the pair (x,y)
            position = (self.get_available_x(next_board, y), y)
            # Add the symbol in a possible position
            next_board[position] = enemy_symbol
            if self.action_check(next_board, enemy_symbol):
                # print("Return a position to not lose")
                return y

        # print("Return a classical position")
        # Perform the traditional action according to the exploration/exploitation technique
        if np.random.uniform(0, 1) < self.exp_rate:
            # Take a random action
            idx = np.random.choice(len(positions))
            action = positions[idx]
        else:
            valueMax = -999
            action = None
            for y in positions:
                # Make a copy of the board
                next_board = board.copy()
                # Save the pair (x,y)
                position = (self.get_available_x(next_board, y), y)
                # Add the symbol in a possible position
                next_board[position] = self.symbol
                # Take the next board hash
                next_boardHash = self.getHash(next_board)
                value = 0 if self.states_value.get(next_boardHash) is None \
                    else self.states_value.get(next_boardHash)
                # print("Value: " , value)
                if value >= valueMax:
                    valueMax = value
                    action = y
        # print("{} takes action {}".format(self.name, action))
        return action

    def winner_check(self, board, x, y, x_dir, y_dir):
        """
        Method that check if there are 4 symbols in a line
        :param board: the game board
        :param x: is the x coordinates of the point to check
        :param y: is the y coordinates of the point to check
        :param x_dir: is the x direction of the line to check: 0 vertical, 1 go up
        :param y_dir: is the y direction of the line to check: 0 horizontal, 1 go up
        :return: +4/-4 if a user won, something else otherwise
        """

        # If the check will exceed the board limits
        if x + 3 * x_dir >= board.shape[0] or y + 3 * y_dir >= board.shape[1] or\
                x + 3 * x_dir < 0 or y + 3 * y_dir < 0:
            return 0

        result = 0

        for i in range(4):
            # Add the value of the next cell in the line to check
            result += board[x + i * x_dir, y + i * y_dir]

        return result

    def action_check(self, board, symbol):
        """
        Check the board and search for end game conditions
        :param board: the board game
        :param symbol: symbol to check for
        :return: True if the player with symbol win, False otherwise
        """

        if symbol == CellState.X_Value:
            value = 4
        else:
            value = -4

        # Check if someone won
        for x in range(board.shape[0]):
            for y in range(board.shape[1]):
                if board[x, y] != CellState.empty_Value:

                    if self.winner_check(board, x, y, 1, 0) == value or \
                            self.winner_check(board, x, y, 0, 1) == value or \
                            self.winner_check(board, x, y, 1, 1) == value or \
                            self.winner_check(board, x, y, -1, 1) == value:
                        return True

        # If no winner
        return False

    def addState(self, state):
        """
        Add the new state in the list
        :param state: is the new state after the action
        :return: nothing
        """
        self.states.append(state)

    def feedReward(self, reward):
        """
        Back propagation of the reward received during the current game
        :param reward: is the reward sent after the end of the game accordingly to the result
        :return: nothing
        """
        # print("Updating value")
        next_state = None
        # print("In order states are: ", self.states)
        # print("Reversed states are: ", [x for x in reversed(self.states)])
        for state in reversed(self.states):
            # If it's a new state never visited before
            if self.states_value.get(state) is None:
                self.states_value[state] = 0
            if next_state is not None:
                # Update the existing value using reinforcement learning formula
                self.states_value[state] = (1 - self.lr) * self.states_value[state] \
                                           + self.lr * (reward + self.gamma * self.states_value[next_state])
            else:
                # Update the existing value using reinforcement learning formula
                self.states_value[state] = (1 - self.lr) * self.states_value[state] + self.lr * reward
            # Save the current state to use it in the next iteration
            next_state = state

    def reset(self):
        """
        Reset the states of the current game for the next game
        :return: nothing
        """
        self.states = []

    def savePolicy(self):
        """
        Method that saves the new updated policy of the player
        :return: nothing
        """
        print("Saving configuration...")
        file = open('Files/policy_' + str(self.name), 'wb')
        pickle.dump(self.states_value, file)
        file.close()
        print("Configuration saved!")

    def loadPolicy(self, f):
        """
        Method that loads the policy of the player before starting the game
        :param f: is the path of the file
        :return: nothing
        """
        print("Loading policy...")
        if Path(f).is_file():
            file = open(f, 'rb')
            self.states_value = pickle.load(file)
            file.close()
            print("Policy loaded")
        else:
            print("Error in uploading the policy")


class HumanPlayer(Player):
    def __init__(self, name, symbol):
        super().__init__(name, symbol)

    def chooseAction(self, positions):
        """
        Method that asks the HumanPlayer to choose the board's position on which perform the action
        :param positions: is the list with all the available positions
        :return: the action chose -> an integer containing the column the player chose
        """
        while True:
            try:
                col = int(input("Input your action col: "))
                if type(col) != int:
                    raise Exception()
            except Exception:
                print("Wrong format, insert again!")
                continue

            # If col is a valid integer position
            if col in positions:
                return col

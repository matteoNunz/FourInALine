"""
Date: 19/09/2022
Author: Matteo Nunziante
Description: Four In A Line game
Example of reinforcement learning applied to a game:
    -> it's possible to train 2 players (one that start first and one that start for second)
    -> the training can be between the 2 artificial player and also during the game with a human player
"""

from enum import IntEnum


class CellState(IntEnum):
    """
    State of the board cell
    O_Value -> O
    X_Value -> X
    empty_Value -> empty cell
    """
    O_Value = -1,
    X_Value = 1,
    empty_Value = 0


class GameState(IntEnum):
    """
    State of the game
    WIN -> if the first player won
    LOOSE -> if the first player lose
    DRAW -> if the game ended but nobody won
    UNDEFINED -> if the game is still open
    """
    WIN = 0,
    LOOSE = 1,
    DRAW = 2,
    UNDEFINED = 3

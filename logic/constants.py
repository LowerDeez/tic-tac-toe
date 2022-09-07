from enum import Enum

DEFAULT_BOARD_SIZE = 3

MAX_PLAYERS_COUNT = 2

EMPTY_LABEL = ""

WINNER_MESSAGE = "You won, player {player}!"

LOSS_MESSAGE = "The player {player} won!"

GAME_TIED_MESSAGE = "The game is tied. Try again!"

CLOSED_GAME_MESSAGE = "{player} player left the game!"

GAME_STARTED_MESSAGE = "Game started!"

YOUR_MOVE_PLAYER_MESSAGE = "Next move is yours {player}"

NEXT_MOVE_FOR_PLAYER_MESSAGE = "Next move for player {player}"


class GameAction(str, Enum):
    CREATE = 'create'
    NEW = 'new'
    JOIN = 'join'
    CLOSE = 'close'
    MOVE = 'move'
    FINISH = 'finish'

    @classmethod
    def values(cls):
        return [e for e in GameAction]


class PlayerState(str, Enum):
    X = "X"
    O = "O"

    @classmethod
    def opposite(cls, state: "PlayerState"):
        return next(value for value in PlayerState if value != state)

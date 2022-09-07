class GameException(Exception):
    pass


class GameAlreadyFilled(GameException):
    pass


class PlayerAlreadyInGame(GameException):
    pass

from logic.constants import PlayerState
from logic.types import Notifier
from logic.game.entities import Player


async def create_player(state: PlayerState, notifier: Notifier) -> Player:
    return Player(state=state, notifier=notifier)

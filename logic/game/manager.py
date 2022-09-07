import typing
from dataclasses import dataclass, field

from logic.game.entities import Game, Player
from logic.game.services.game import create_game, add_player_to_game, activate_game
from logic.types import Notifier
from logic.game.services.player import create_player
from logic.constants import PlayerState


@dataclass
class GamesManager:
    """
    Manages a batch of games
    """
    games: typing.Dict[str, Game] = field(default_factory=dict)

    async def create(self, notifier: Notifier, game_id: str) -> Game:
        first_player = await create_player(state=PlayerState.X, notifier=notifier)
        game = await create_game(player=first_player, game_id=game_id)
        print("MOVES:", game.board)
        print("WINNING COMBOS:", game.winning_combos)
        print("CELLS", game.cells)
        self.games[game_id] = game
        return game

    async def join(self, game_id: str, notifier: Notifier) -> Game | None:
        """
        Selects game by a given number
        Adds second player to this game
        Moves game to playing from created
        """
        game = self.games.get(game_id)

        if game:
            new_player = await create_player(state=PlayerState.O, notifier=notifier)
            await add_player_to_game(game=game, player=new_player)
            await activate_game(game=game)
            return game

    async def get(self, game_id: str) -> Game | None:
        """
        Return game
        """
        return self.games.get(game_id)

    async def remove(self, game_id: str) -> None:
        """
        Removes all games with user, who has a given notifier
        """
        game = self.games.pop(game_id, None)

        if game:
            del game

    async def clear(self, notifier: Notifier) -> typing.List[Player]:
        """
        Removes all games with user, who has a given notifier
        """
        games_to_remove = []
        players = []

        for game in self.games.values():
            for player in game.players:
                if player.notifier == notifier:
                    games_to_remove.append(game)

        for game in games_to_remove:
            players.extend(game.players)
            self.games.pop(game.id)
            del game

        return players

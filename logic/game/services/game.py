from logic.constants import MAX_PLAYERS_COUNT
from logic.exceptions import GameAlreadyFilled, PlayerAlreadyInGame
from logic.game.entities import Game, Player


async def validate_game(game: Game, player: Player):
    if len(game.players) >= 2:
        raise GameAlreadyFilled()

    if player in game.players:
        raise PlayerAlreadyInGame()


async def create_game(player: Player, game_id: str) -> Game:
    game = Game(current_player=player, id=game_id)
    game.current_player = player
    game.players.append(player)
    return game


async def activate_game(game: Game):
    if len(game.players) == MAX_PLAYERS_COUNT:
        game.is_active = True
    else:
        game.is_active = False


async def add_player_to_game(game: Game, player: Player) -> Game:
    await validate_game(game=game, player=player)
    game.players.append(player)
    return game

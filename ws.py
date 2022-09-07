from dataclasses import asdict, dataclass
import typing

from starlette.websockets import WebSocket

from logic.constants import (
    GameAction,
    PlayerState,
    WINNER_MESSAGE,
    LOSS_MESSAGE,
    GAME_TIED_MESSAGE,
    CLOSED_GAME_MESSAGE,
    GAME_STARTED_MESSAGE,
    YOUR_MOVE_PLAYER_MESSAGE,
    NEXT_MOVE_FOR_PLAYER_MESSAGE,
)
from logic.game.manager import GamesManager
from helpers.ws import WebSocketBroadcast
from logic.game.entities import Game


@dataclass
class GameInfo:
    games: typing.Dict[str, Game]
    action: GameAction
    player: str = None
    other_player: str = None
    is_player_move: bool = None
    winner: PlayerState = None
    has_winner: bool = None
    is_tied: bool = None
    message: str = None

    def __post_init__(self):
        self.games = list(self.games.keys())

    def to_data(self, **additional_info) -> typing.Dict:
        data = asdict(self)
        data.update(additional_info)
        data = {key: value for key, value in data.items() if value is not None}
        return data


class WebSockerGameWrapper(WebSocketBroadcast):
    """
    WebSocket wrapper for Tic Tac Toe game logic
    Handles logic for actions, which can be sent from FE side
    """
    encoding = "json"
    actions: typing.List = GameAction.values()
    game_manager = GamesManager()

    async def new(self, websocket: WebSocket, data: typing.Dict):
        info = GameInfo(action=GameAction.NEW, games=self.game_manager.games)
        await websocket.send_json(data=info.to_data())

    async def create(self, websocket: WebSocket, data: typing.Dict):
        await self.game_manager.create(notifier=websocket, game_id=data["game_id"])
        info = GameInfo(action=GameAction.CREATE, games=self.game_manager.games)
        # notify other users about created games
        await self.manager.broadcast_exclude(to_exclude=[websocket], message=info.to_data())

    async def join(self, websocket: WebSocket, data: typing.Dict):
        game = await self.game_manager.join(game_id=data["game_id"], notifier=websocket)

        if game is None:
            await websocket.send_json({'action': 'error', 'message': 'The game has been started'})
            return

        for player in game.players:
            opposite_player = game.find_player(state=PlayerState.opposite(state=player.state))

            info = GameInfo(
                action=GameAction.JOIN,
                games=self.game_manager.games,
                player=player.state,
                other_player=opposite_player.state,
                is_player_move=player.state == PlayerState.X,
                message=(
                    YOUR_MOVE_PLAYER_MESSAGE
                    if player.state == PlayerState.X
                    else NEXT_MOVE_FOR_PLAYER_MESSAGE
                ).format(player=PlayerState.X)
            )
            await player.notifier.send_json(data=info.to_data())

    async def move(self, websocket: WebSocket, data: typing.Dict):
        game = await self.game_manager.get(game_id=data["game_id"])
        state = data["state"]
        print("MOVE GAME:", game)

        if game is None:
            await websocket.send_json({'action': 'error', 'message': 'The game was closed'})
            return

        cell = data["cell"]
        move = game.process_move(cell=cell, state=state)

        for player in game.players:
            opposite_state = PlayerState.opposite(state=state)
            is_player_move = player.notifier != websocket
            move_info = GameInfo(
                action=GameAction.MOVE,
                games=self.game_manager.games,
                is_player_move=is_player_move,
                message=(
                    YOUR_MOVE_PLAYER_MESSAGE
                    if player.state == opposite_state
                    else NEXT_MOVE_FOR_PLAYER_MESSAGE
                ).format(player=opposite_state)
            )
            await player.notifier.send_json(data=move_info.to_data(cell=cell, state=move.state))

        # notify players if someone won or the game is tied
        if not game.is_active:
            players = game.players
            has_winner = game.has_winner
            winner = game.winner.state if game.winner else None
            is_tied = game.is_tied()

            for player in players:
                message = (
                    GAME_TIED_MESSAGE if is_tied
                    else (WINNER_MESSAGE if player.state == winner else LOSS_MESSAGE).format(player=winner)
                )

                info = GameInfo(
                    action=GameAction.FINISH,
                    games=self.game_manager.games,
                    is_player_move=False,
                    winner=winner,
                    has_winner=has_winner,
                    is_tied=is_tied,
                    message=message,
                )
                await player.notifier.send_json(data=info.to_data())

    async def close(self, websocket: WebSocket, data: typing.Dict):
        game_id = data["game_id"]
        state_of_left = data["state"]

        game = await self.game_manager.get(game_id=game_id)
        left_player = game.find_player(state=state_of_left)
        await self.game_manager.remove(game_id=data["game_id"])

        info = GameInfo(
            action=GameAction.CLOSE,
            games=self.game_manager.games,
        )
        await left_player.notifier.send_json(data=info.to_data())

        abandoned_player = game.find_player(state=PlayerState.opposite(state=state_of_left))

        if abandoned_player:
            # added message for abandoned player
            info.message = CLOSED_GAME_MESSAGE.format(player=state_of_left)
            await abandoned_player.notifier.send_json(data=info.to_data())

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        await self.game_manager.clear(notifier=websocket)
        await super().on_disconnect(websocket, close_code=close_code)

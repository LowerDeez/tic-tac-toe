import typing
from dataclasses import dataclass, field

from logic.constants import DEFAULT_BOARD_SIZE, EMPTY_LABEL, PlayerState
from logic.types import Notifier


@dataclass
class Player:
    state: PlayerState
    notifier: Notifier

    def __eq__(self, other):
        return self.state == other.state


@dataclass
class Move:
    row: int
    col: int
    state: PlayerState | str = EMPTY_LABEL


@dataclass
class Game:
    id: str
    current_player: Player | None = None
    is_active: bool = False
    players: typing.List[Player] = field(default_factory=list)
    board_size: int = DEFAULT_BOARD_SIZE
    board: typing.List[typing.List[Move]] = field(init=False)
    winning_combos: typing.List[typing.List[typing.Tuple]] = field(init=False)
    cells: typing.Dict[int, typing.Tuple[int, int]] = field(init=False)
    has_winner: bool = False
    winner_combo: typing.List[typing.Tuple] = field(default_factory=list)
    winner: Player = None

    def __post_init__(self):
        self.board = self.generate_board()
        self.winning_combos = self.generate_winning_combos()
        self.cells = self.generate_cells()

    def generate_board(self) -> typing.List[typing.List[Move]]:
        return [
            [Move(row, col) for col in range(self.board_size)]
            for row in range(self.board_size)
        ]

    def generate_winning_combos(self) -> typing.List[typing.List[typing.Tuple]]:
        # e.g. [[(0, 0), (0, 1), (0, 2)], ...]
        rows = [
            [(move.row, move.col) for move in row]
            for row in self.board
        ]
        print("ROWS:", rows)

        # e.g. [[(0, 0), (1, 0), (2, 0)], ...]
        columns = [list(col) for col in zip(*rows)]
        print("COLUMNS", columns)

        # e.g. [(0, 0), (1, 1), (2, 2)]
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        print("FIRST DIAGONAL:", first_diagonal)

        # e.g. [(0, 2), (1, 1), (2, 0)]
        second_diagonal = [col[j] for j, col in enumerate(reversed(columns))]  # reverse simplifies the logic to get the second diagonal
        print("SECOND DIAGONAL:", second_diagonal)

        return rows + columns + [first_diagonal, second_diagonal]

    def generate_cells(self) -> typing.Dict[int, typing.Tuple[int, int]]:
        """
        Maps indexes to cells coordinates
        """
        index = 0
        cells = {}

        for row in range(self.board_size):
            for col in range(self.board_size):
                cells[index] = (row, col)
                index += 1

        return cells

    def process_move(self, cell: int, state: PlayerState) -> Move:
        row, col = self.cells.get(cell)
        move = Move(row=row, col=col, state=state)
        self.board[move.row][move.col] = move
        self.current_player = self.find_player(state=state)

        # TODO: check winning combo after some amount of views?
        # check each winning combo if all it's states are equal to the current move state
        for combo in self.winning_combos:
            results = set(
                self.board[row][col].state
                for row, col in combo
            )

            is_win = len(results) == 1 and EMPTY_LABEL not in results

            if is_win:
                self.is_active = False
                self.has_winner = True
                self.winner_combo = combo
                self.winner = next(player for player in self.players if player.state == move.state)
                break

        return move

    def is_tied(self) -> bool:
        """Return True if the game is tied, and False otherwise."""
        no_winner = not self.has_winner
        played_moves = (
            move.state for row in self.board for move in row
        )
        # check if all board are not equal to empty string
        is_tied = no_winner and all(played_moves)

        if is_tied:
            self.is_active = False

        return is_tied

    def find_player(self, state: PlayerState) -> Player | None:
        for player in self.players:
            if player.state == state:
                return player

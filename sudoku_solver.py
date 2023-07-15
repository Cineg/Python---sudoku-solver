import copy
import random
from enum import Enum

GRID_SIZE = 9
BLANK_GRID = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]


class Difficulty(Enum):
    Easy = 2
    Medium = 4
    Hard = 6


def print_formatted_sudoku_grid(sudoku_board: list):
    for row_index, row in enumerate(sudoku_board):
        formatted_row = ""
        for column_index, item in enumerate(row):
            if (column_index) % 3 == 0 and column_index != 0:
                formatted_row += " | "

            formatted_row += f" {item} "

        if row_index % 3 == 0 and row_index != 0:
            print("-" * len(formatted_row))
        else:
            print(" " * len(formatted_row))

        print(formatted_row)


def check_valid_option(number: int, sudoku_board: list, position: tuple) -> bool:
    row = sudoku_board[position[0]]
    column = [sudoku_board[row_index][position[1]] for row_index in range(GRID_SIZE)]
    square = []

    start_row = position[0] - position[0] % 3
    start_col = position[1] - position[1] % 3
    for row_index in range(start_row, start_row + 3):
        for col_index in range(start_col, start_col + 3):
            square.append(sudoku_board[row_index][col_index])

    return (
        number not in set(row)
        and number not in set(column)
        and number not in set(square)
    )


def solve_board(sudoku_board: list) -> bool:
    for row_index, row in enumerate(sudoku_board):
        for column_index, item in enumerate(row):
            if item == 0:
                backtrack_solve((row_index, column_index), sudoku_board)

            if sudoku_board[row_index][column_index] == 0:
                return False

    return True


def backtrack_solve(coordinates: tuple, sudoku_board: list):
    for number in range(1, GRID_SIZE + 1):
        if check_valid_option(number, sudoku_board, coordinates):
            sudoku_board[coordinates[0]][coordinates[1]] = number

            if not solve_board(sudoku_board):
                sudoku_board[coordinates[0]][coordinates[1]] = 0


def generate_sudoku_board(
    difficulty: Difficulty = Difficulty.Medium, board: list = None
) -> list:
    if board == None:
        board_copy = generate_solvable_board()
    else:
        board_copy = copy.deepcopy(board)

    return prepare_board(board_copy, difficulty.value)


def generate_solvable_board() -> list:
    board = copy.deepcopy(BLANK_GRID)

    i = 0
    while i < GRID_SIZE:
        row = random.randint(
            0, GRID_SIZE - 6
        )  # generate values in couple of rows, not all board;
        col = random.randint(0, GRID_SIZE - 1)
        value = random.randint(1, GRID_SIZE)

        if not check_valid_option(value, board, (row, col)):
            board[row][col] = 0
            i -= 1

        else:
            board[row][col] = value

        i += 1

    if not solve_board(board):
        raise ValueError("The sudoku board is unsolvable.")

    return board


def prepare_board(board: list, fields_to_remove: int):
    i = 0
    while i < fields_to_remove * GRID_SIZE:
        row = random.randint(0, GRID_SIZE - 1)
        col = random.randint(0, GRID_SIZE - 1)

        if board[row][col] != 0:
            board[row][col] = 0
            i += 1

    return board


def main():
    board = generate_sudoku_board(Difficulty.Easy)
    print_formatted_sudoku_grid(board)


if __name__ == "__main__":
    pass

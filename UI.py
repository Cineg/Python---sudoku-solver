from sudoku_solver import (
    Difficulty,
    generate_solvable_board,
    generate_sudoku_board,
)
from datetime import datetime
import pygame


# global settings
BG_COLOR = (11, 13, 8)
TEXT_COLOR = (242, 242, 242)
THICK_LINE = 5
SLIM_LINE = 1


class Button:
    def __init__(
        self,
        window: pygame.Surface,
        button_text: str,
        on_click_value,
        draw_position: tuple,
    ):
        """
        draw_position = top-left corner of button.
        """
        self.window = window
        self.width = 120
        self.height = 45
        self.border_radius = 20
        self.position = self.get_position(draw_position)
        self.value = on_click_value
        self.text = button_text
        self.font_size = 30
        self.font_name = None
        self.font = pygame.font.Font(self.font_name, self.font_size)

    def clicked(self, coordinates):
        click_x, click_y = coordinates
        start_x, start_y, end_x, end_y = self.position

        if (
            click_x >= start_x
            and click_x <= end_x
            and click_y >= start_y
            and click_y <= end_y
        ):
            return self.value

    def get_position(self, position) -> tuple:
        if len(position) == 2:
            x, y = position
        else:
            x, y, _, __ = position

        return (x, y, x + self.width, y + self.height)

    def change_font(self, font_name: str = None, font_size: int = None):
        if font_name != None:
            self.font_name = font_name

        if font_size != None:
            self.font_size = font_size

        self.font = pygame.font.Font(self.font_name, self.font_size)

    def change_size(
        self, width: int = None, height: int = None, border_radius: int = None
    ):
        if width != None:
            self.width = width

        if height != None:
            self.height = height

        if border_radius != None:
            self.border_radius = border_radius

        self.position = self.get_position(self.position)

    def change_text(self, text: str):
        self.text = text

    def draw(self):
        text = self.font.render(self.text, True, TEXT_COLOR)
        start_x, start_y, end_x, end_y = self.position

        pygame.draw.rect(
            window,
            TEXT_COLOR,
            (start_x, start_y, self.width, self.height),
            3,
            self.border_radius,
        )

        centered_text = (
            (start_x + end_x) / 2 - (text.get_width() // 2),
            (start_y + end_y) / 2 - (text.get_height() // 2),
        )
        window.blit(text, centered_text)


class Timer:
    def __init__(self, window: pygame.Surface):
        self.window = window
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None

    def start_timer(self):
        self.start_time = datetime.now()
        self.end_time = None

    def stop_timer(self):
        if self.end_time == None:
            self.end_time = datetime.now()

    def get_elapsed_time(self):
        if self.start_time == None:
            return

        if self.end_time == None:
            end_time = datetime.now()
        else:
            end_time = self.end_time

        self.elapsed_time = end_time - self.start_time

    def draw(self, position: tuple = None):
        self.get_elapsed_time()
        time_formatted = self.format_time()
        font = pygame.font.Font(None, 25)
        text = font.render(f"Elapsed time: {time_formatted}", True, TEXT_COLOR)

        if position == None:
            ## draw timer at bottom-right
            x = window.get_width() - text.get_width() - 10
            y = window.get_height() - text.get_height() - 10
            position = (x, y)

        window.blit(text, position)

    def format_time(self) -> str:
        """
        Returns time in "mm:ss" format
        """
        if self.elapsed_time == None:
            return "00:00"

        minutes = int(self.elapsed_time.total_seconds() // 60)
        seconds = int(self.elapsed_time.total_seconds() % 60)

        return f"{minutes:02d}:{seconds:02d}"


class Board:
    cells = []

    def __init__(
        self, window: pygame.Surface, difficulty: Difficulty = Difficulty.Medium
    ):
        self.window = window
        self.solved_board = generate_solvable_board()
        self.total_board_width = window.get_width()
        self.cell_line_size = self.total_board_width / 9
        self.board = generate_sudoku_board(difficulty, self.solved_board)
        self.selected = None
        self.current_selected = None
        self.is_draft_enabled = False
        self.is_completed = False
        self.mistakes_count = 0

    def reload_board(self, difficulty: Difficulty):
        if difficulty == None:
            return

        self.solved_board = generate_solvable_board()
        self.board = generate_sudoku_board(difficulty, self.solved_board)
        self._create_cells()
        self.is_completed = False
        self.mistakes_count = 0

    def draw(self):
        self._draw_grid()
        self._draw_mistakes_counter()

        if self.cells == None:
            return

        if self.is_completed:
            color = (242, 159, 5)
        else:
            color = None

        for row in self.cells:
            for cell in row:
                cell.draw(color)

    def mouse_select(self, coordinates: tuple):
        if len(self.cells) == 0:
            return
        if self.selected == None:
            self.selected = (0, 0)

        row = int(coordinates[0] // self.cell_line_size)
        column = int(coordinates[1] // self.cell_line_size)

        if row > 8 or row < 0:
            return
        if column > 8 or column < 0:
            return

        self.cells[self.selected[0]][self.selected[1]].select(False)

        self.selected = (row, column)
        self.cells[self.selected[0]][self.selected[1]].select(True)

    def keyboard_select(self, coordinates: tuple):
        if len(self.cells) == 0:
            return

        if self.selected == None:
            self.selected = (0, 0)

        new_position = (
            self.selected[0] + coordinates[0],
            self.selected[1] + coordinates[1],
        )
        new_position = self._get_bounds(new_position)

        self.cells[self.selected[0]][self.selected[1]].select(False)
        self.cells[new_position[0]][new_position[1]].select(True)

        self.selected = new_position

    def input_value(self, value: int):
        if self.selected == None:
            return

        cell = self.cells[self.selected[0]][self.selected[1]]
        if self.is_draft_enabled:
            # not sure if game isn't too easy with this one
            possibilities = self.get_possibilities(self.selected)
            if value not in possibilities:
                cell.add_draft(value)

        # add value to the board if correct
        else:
            if cell.value != 0:
                return

            if value == self.solved_board[self.selected[0]][self.selected[1]]:
                self.board[self.selected[0]][self.selected[1]] = value
                cell.add_value(value)
            else:
                self.mistakes_count += 1

    def get_possibilities(self, coordinates: tuple) -> dict:
        row = self.board[coordinates[0]]
        column = [
            self.board[row_index][coordinates[1]]
            for row_index in range(len(self.board))
        ]
        square = []

        start_row = coordinates[0] - coordinates[0] % 3
        start_col = coordinates[1] - coordinates[1] % 3
        for row_index in range(start_row, start_row + 3):
            for col_index in range(start_col, start_col + 3):
                square.append(self.board[row_index][col_index])

        possibilities = {}

        # need to exclude 0
        possibilities[0] = 0
        for item in row:
            if item not in possibilities:
                possibilities[item] = item

        for item in column:
            if item not in possibilities:
                possibilities[item] = item

        for item in square:
            if item not in possibilities:
                possibilities[item] = item

        return possibilities

    def change_draft_mode(self) -> str:
        self.is_draft_enabled = not self.is_draft_enabled

        if self.is_draft_enabled:
            on_off = "On"
        else:
            on_off = "Off"

        return f"Draft Mode {on_off}"

    def check_completion(self) -> bool:
        if self.board == self.solved_board:
            self.is_completed = True

        return self.is_completed

    # Private functions
    def _draw_grid(self):
        for i in range(len(self.board) + 1):
            if i % 3 == 0 and i != 0:
                line_thickness = THICK_LINE
            else:
                line_thickness = SLIM_LINE

            # Rows
            pygame.draw.line(
                self.window,
                TEXT_COLOR,
                (0, i * self.cell_line_size),
                (self.total_board_width, i * self.cell_line_size),
                line_thickness,
            )

            # Columns
            pygame.draw.line(
                self.window,
                TEXT_COLOR,
                (i * self.cell_line_size, 0),
                (i * self.cell_line_size, self.total_board_width),
                line_thickness,
            )

    def _draw_mistakes_counter(self):
        font = pygame.font.Font(None, 50)
        color = (187, 0, 0)

        if self.mistakes_count < 5:
            string = " X " * self.mistakes_count
        else:
            string = f"Mistakes count: {self.mistakes_count}"
            
        text = font.render(string, True, color)
        coordinates = (
            self.total_board_width - (text.get_width() + 20),
            self.total_board_width + 20,
        )

        self.window.blit(text, coordinates)

    def _get_bounds(self, position: tuple) -> tuple:
        if position[0] == -1:
            return (0, position[1])

        if position[0] == 9:
            return (8, position[1])

        if position[1] == -1:
            return (position[0], 0)

        if position[1] == 9:
            return (position[0], 8)

        return position

    def _create_cells(self):
        cells = []
        rows, columns = len(self.board), len(self.board)
        for row in range(rows):
            row_cells = []
            for col in range(columns):
                cell = Sudoku_Cell(self.window, (row, col), self.board[row][col])
                row_cells.append(cell)
            cells.append(row_cells)
        self.cells = cells


class Sudoku_Cell:
    TEMPORARY_COLOR = (191, 181, 180)
    SELECTED_COLOR = (103, 205, 235)

    def __init__(self, window: pygame.Surface, position: tuple, value: int):
        self.width = window.get_width() / 9
        self.height = window.get_width() / 9
        self.inner_square_size = self.width / 3
        self.row = position[0]
        self.column = position[1]
        self.value = value
        self.temporary_value = {}
        self.selected = False

    def draw(self, color: tuple = None):
        start_position = (self.width * self.row, self.height * self.column)
        end_position = (
            (self.row + 1 * self.width),
            (self.column + 1 * self.height),
        )

        # draw drafts
        if self.value == 0 and len(self.temporary_value) > 0:
            self._draw_drafts(start_position)

        if self.value != 0:
            if color == None:
                color = TEXT_COLOR

            font = pygame.font.Font(None, 80)
            text = font.render(f"{self.value}", True, color)

            window.blit(
                text,
                self._center_text(
                    start_position, end_position, (text.get_width(), text.get_height())
                ),
            )

        # draw selection
        if self.selected:
            pygame.draw.rect(
                window, self.SELECTED_COLOR, (start_position, end_position), THICK_LINE
            )

    def _center_text(self, start: tuple, end: tuple, text_size: tuple) -> tuple:
        return (
            start[0] + end[0] / 2 - (text_size[0] / 2),
            start[1] + end[1] / 2 - (text_size[1] / 2),
        )

    def _draw_drafts(self, start_position):
        font = pygame.font.Font(None, 24)

        for cell in range(10):
            cell_column = (cell - 1) % 3
            cell_row = (cell - 1) // 3

            if cell in self.temporary_value:
                text = font.render(f"{cell}", True, self.TEMPORARY_COLOR)

                text_position = (
                    cell_column * self.inner_square_size
                    + start_position[0]
                    + (text.get_width() / 2),
                    cell_row * self.inner_square_size
                    + start_position[1]
                    + (text.get_height() / 2),
                )

                window.blit(text, text_position)

    # Properties
    def select(self, select: bool):
        self.selected = select

    def add_value(self, value: int):
        self.value = value

    def add_draft(self, value: int):
        if value in self.temporary_value:
            self.temporary_value.pop(value)
        else:
            self.temporary_value[value] = value


def get_button_value(click_position: tuple, *buttons: Button) -> Difficulty:
    for button in buttons:
        clicked_val = button.clicked(click_position)
        if clicked_val != None:
            return clicked_val

    return None


def handle_ingame_input(
    board: Board, timer: Timer, event: pygame.event, *buttons: Button
):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
            board.keyboard_select((-1, 0))

        if event.key == pygame.K_RIGHT:
            board.keyboard_select((1, 0))

        if event.key == pygame.K_UP:
            board.keyboard_select((0, -1))

        if event.key == pygame.K_DOWN:
            board.keyboard_select((0, 1))

        if event.key == pygame.K_d:
            board.change_draft_mode()

        if event.key == pygame.K_r:
            board.reload_board(Difficulty.Medium)
            timer.start_timer()

        if event.key == pygame.K_1 or event.key == pygame.K_KP_1:
            board.input_value(1)
        if event.key == pygame.K_2 or event.key == pygame.K_KP_2:
            board.input_value(2)
        if event.key == pygame.K_3 or event.key == pygame.K_KP_3:
            board.input_value(3)
        if event.key == pygame.K_4 or event.key == pygame.K_KP_4:
            board.input_value(4)
        if event.key == pygame.K_5 or event.key == pygame.K_KP_5:
            board.input_value(5)
        if event.key == pygame.K_6 or event.key == pygame.K_KP_6:
            board.input_value(6)
        if event.key == pygame.K_7 or event.key == pygame.K_KP_7:
            board.input_value(7)
        if event.key == pygame.K_8 or event.key == pygame.K_KP_8:
            board.input_value(8)
        if event.key == pygame.K_9 or event.key == pygame.K_KP_9:
            board.input_value(9)

    if event.type == pygame.MOUSEBUTTONDOWN:
        click_position = pygame.mouse.get_pos()
        board.mouse_select(click_position)

        clicked_button_value = get_button_value(click_position, *buttons)
        if clicked_button_value == None:
            return

        if clicked_button_value == "Draft":
            text = board.change_draft_mode()

            for button in buttons:
                if button.value == "Draft":
                    button.change_text(text)

        else:
            board.reload_board(clicked_button_value)
            timer.start_timer()


def draw_objects(*objects):
    for object in objects:
        object.draw()


def main(window: pygame.Surface):
    # Create items
    timer = Timer(window)
    board = Board(window)

    easy_button = Button(
        window, "Easy", Difficulty.Easy, (10, window.get_height() - 165)
    )

    medium_button = Button(
        window, "Medium", Difficulty.Medium, (10, window.get_height() - 110)
    )

    hard_button = Button(
        window, "Hard", Difficulty.Hard, (10, window.get_height() - 55)
    )

    draft_mode_button = Button(
        window, "Draft Mode Off", "Draft", (140, window.get_height() - 55)
    )
    draft_mode_button.change_size(180)

    # main game loop
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            handle_ingame_input(
                board,
                timer,
                event,
                easy_button,
                medium_button,
                hard_button,
                draft_mode_button,
            )

        if board.check_completion():
            timer.stop_timer()

        # actual render
        window.fill(BG_COLOR)
        draw_objects(
            board, timer, easy_button, medium_button, hard_button, draft_mode_button
        )
        pygame.display.update()


if __name__ == "__main__":
    window_size = (600, 800)
    window = pygame.display.set_mode(window_size)
    pygame.init()
    main(window)
    pygame.quit()

import sys

import pygame
import numpy

from source.constants import SCREEN_HEIGHT, SCREEN_WIDTH, CAPTION, FPS, CELLS_NUMBER, DARK_COLOR, LIGHT_COLOR, \
    FIGURE_COLOR, FIGURE_WIDTH, EMPTY_POSITION, WIN_MASKS


class Game:
    def __init__(self) -> None:
        self._screen_ = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._clock_ = pygame.time.Clock()

        self._cells_ = [pygame.FRect((0, 0), (0, 0)) for _ in range(CELLS_NUMBER ** 2)]

        self._figures_to_display_: list[tuple[tuple[int, int], str], ...] = [EMPTY_POSITION for _ in
                                                                             range(CELLS_NUMBER ** 2)]
        self._figures_ = [0xFF for _ in range(CELLS_NUMBER ** 2)]

        self._figure_names_ = ["cross", "nod"]
        self._current_figure_ = 0

        self._game_running_ = True
        self._winner_ = ""

        pygame.display.set_caption(CAPTION)

    def fill_board(self) -> None:
        cell_width = SCREEN_WIDTH // CELLS_NUMBER
        cell_height = SCREEN_HEIGHT // CELLS_NUMBER

        for i in range(CELLS_NUMBER):
            for j in range(CELLS_NUMBER):
                self._cells_[i * CELLS_NUMBER + j] = pygame.FRect((i * cell_width, j * cell_height),
                                                                  (cell_width, cell_height))

    def draw_board(self) -> None:
        for i in range(CELLS_NUMBER):
            for j in range(CELLS_NUMBER):
                index = i * CELLS_NUMBER + j

                if index % 2:
                    pygame.draw.rect(self._screen_, DARK_COLOR, self._cells_[index])
                else:
                    pygame.draw.rect(self._screen_, LIGHT_COLOR, self._cells_[index])

    def draw_figure(self, position: tuple[int | float, int | float], figure_type: str) -> None:
        index = position[0] * CELLS_NUMBER + position[1]

        match figure_type:
            case "nod":
                cell = self._cells_[index]

                pygame.draw.circle(self._screen_, FIGURE_COLOR, cell.center, cell.width * 0.4, width=FIGURE_WIDTH)
            case "cross":
                cell = self._cells_[index]
                cell_x, cell_y = cell.center
                figure_radius = cell.width * 0.4

                pygame.draw.line(self._screen_, FIGURE_COLOR,
                                 (cell_x - figure_radius, cell_y - figure_radius),
                                 (cell_x + figure_radius, cell_y + figure_radius),
                                 width=FIGURE_WIDTH)
                pygame.draw.line(self._screen_, FIGURE_COLOR,
                                 (cell_x - figure_radius, cell_y + figure_radius),
                                 (cell_x + figure_radius, cell_y - figure_radius),
                                 width=FIGURE_WIDTH)
            case _:
                return

    def draw_figures(self) -> None:
        for position, figure in self._figures_to_display_:
            if position == EMPTY_POSITION:
                continue

            self.draw_figure(position, figure)

    def place_figure(self, position: tuple[int, int]) -> None:
        x, y = position

        figure_index_x = x * CELLS_NUMBER // SCREEN_WIDTH
        figure_index_y = y * CELLS_NUMBER // SCREEN_HEIGHT

        index = figure_index_x * CELLS_NUMBER + figure_index_y

        if self._figures_to_display_[index] == EMPTY_POSITION:
            self._figures_to_display_[index] = (
                (figure_index_x, figure_index_y), self._figure_names_[self._current_figure_])
            self._figures_[index] = self._current_figure_

            self._current_figure_ = not self._current_figure_

    def check_win(self) -> None:
        for win_mask in WIN_MASKS:
            accumulator = 0

            for figure, mask in zip(self._figures_, win_mask):
                accumulator += figure & mask

            if accumulator == 0:
                self._game_running_ = False
                self._winner_ = self._figure_names_[0]
            elif accumulator == 3:
                self._game_running_ = False
                self._winner_ = self._figure_names_[1]

    def run(self) -> None:
        self.fill_board()

        while self._game_running_:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    self.place_figure(pygame.mouse.get_pos())

            self.draw_board()
            self.draw_figures()
            self.check_win()

            self._clock_.tick(FPS)
            pygame.display.update()

        print(f"Winner: {self._winner_}")

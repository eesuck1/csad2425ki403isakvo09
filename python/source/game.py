import sys
import threading

import pygame

pygame.init()
pygame.font.init()

from source.communication import Channel
from source.constants import SCREEN_HEIGHT, SCREEN_WIDTH, CAPTION, FPS, CELLS_NUMBER, DARK_COLOR, LIGHT_COLOR, \
    FIGURE_COLOR, FIGURE_WIDTH, EMPTY_POSITION, WIN_MASKS, PSOC_ADDRESS, MAN_VS_MAN_PACKET, MAN_VS_AI_PACKET, \
    AI_VS_AI_PACKET, ACK_PACKET, RESET_PACKET


class Game:
    def __init__(self) -> None:
        self._bleak_thread_ = None
        self._channel_ = Channel(PSOC_ADDRESS)

        self._screen_ = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._clock_ = pygame.time.Clock()

        self._cells_ = [pygame.FRect((0, 0), (0, 0)) for _ in range(CELLS_NUMBER ** 2)]

        self._figures_to_display_: list[tuple[tuple[int, int], str], ...] = [EMPTY_POSITION for _ in
                                                                             range(CELLS_NUMBER ** 2)]
        self._figures_ = [0xFF for _ in range(CELLS_NUMBER ** 2)]

        self._figure_names_ = ["cross", "nod"]
        self._current_figure_ = 0

        self._font_ = pygame.font.SysFont("Arial", 24)

        self._mvm_rect_ = pygame.FRect((SCREEN_WIDTH // 10, SCREEN_HEIGHT // 1.25), (SCREEN_WIDTH // 1.25, SCREEN_HEIGHT // 8))
        self._mva_rect_ = pygame.FRect((SCREEN_WIDTH // 10, SCREEN_HEIGHT // 2.25), (SCREEN_WIDTH // 1.25, SCREEN_HEIGHT // 8))
        self._ava_rect_ = pygame.FRect((SCREEN_WIDTH // 10, SCREEN_HEIGHT // 8), (SCREEN_WIDTH // 1.25, SCREEN_HEIGHT // 8))

        self._game_running_ = True
        self._game_packet_send_ = False

        self._click_delay_ = 0

        self._game_type_ = 0
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

    def draw_menu(self) -> None:
        self._screen_.fill(LIGHT_COLOR)

        pygame.draw.rect(self._screen_, DARK_COLOR, self._mvm_rect_)
        pygame.draw.rect(self._screen_, DARK_COLOR, self._mva_rect_)
        pygame.draw.rect(self._screen_, DARK_COLOR, self._ava_rect_)

        self._screen_.blit(self._font_.render("Man VS Man", True, (0, 0, 0)),
                           self._mvm_rect_.center)
        self._screen_.blit(self._font_.render("Man VS AI", True, (0, 0, 0)),
                           self._mva_rect_.center)
        self._screen_.blit(self._font_.render("AI VS AI", True, (0, 0, 0)),
                           self._ava_rect_.center)

    def check_menu(self) -> None:
        mouse_position = pygame.mouse.get_pos()

        if self._mvm_rect_.collidepoint(mouse_position):
            self._game_type_ = 1
            self.send_packet(MAN_VS_MAN_PACKET)
        elif self._mva_rect_.collidepoint(mouse_position):
            self._game_type_ = 2
            self.send_packet(MAN_VS_AI_PACKET)
        elif self._ava_rect_.collidepoint(mouse_position):
            self._game_type_ = 3
            self.send_packet(AI_VS_AI_PACKET)

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

    def send_packet(self, packet: bytes, time_out: int = -1) -> None:
        counter = 0

        while True:
            self._channel_.set_buffer(packet, True)

            received = self._channel_.get_buffer()

            if received == ACK_PACKET or counter == time_out:
                break

            counter += 1

    def run(self) -> None:
        self.fill_board()

        self._bleak_thread_ = threading.Thread(target=self._channel_.run)
        self._bleak_thread_.daemon = True
        self._bleak_thread_.start()

        while self._game_running_:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP and not self._click_delay_:
                    if self._game_type_ == 0:
                        self.check_menu()
                    else:
                        x, y = pygame.mouse.get_pos()

                        figure_index_x = x * CELLS_NUMBER // SCREEN_WIDTH + 1
                        figure_index_y = y * CELLS_NUMBER // SCREEN_HEIGHT + 1

                        self.send_packet(bytes([figure_index_x, figure_index_y]))
                        # self.place_figure(pygame.mouse.get_pos())

                    self._click_delay_ = FPS // 3
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        print("Reset Sent")

                        self.send_packet(RESET_PACKET)
                        self._game_type_ = 0

            match self._game_type_:
                case 0:
                    self.draw_menu()
                case 1:
                    self.draw_board()
                    self.draw_figures()
                    self.check_win()
                case 2:
                    self.draw_board()
                    self.draw_figures()
                    self.check_win()
                case 3:
                    self.draw_board()
                    self.draw_figures()
                    self.check_win()

            packet = self._channel_.get_buffer()

            if self._click_delay_:
                self._click_delay_ -= 1

            if packet:
                print(f"[INFO] Received Packet: {packet}")

            self._clock_.tick(FPS)
            pygame.display.update()

        print(f"Winner: {self._winner_}")

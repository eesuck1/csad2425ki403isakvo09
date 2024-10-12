import sys

import pygame

pygame.init()
pygame.font.init()

from source.communication import Channel
from source.constants import SCREEN_HEIGHT, SCREEN_WIDTH, CAPTION, FPS, CELLS_NUMBER, DARK_COLOR, LIGHT_COLOR, \
    FIGURE_COLOR, FIGURE_WIDTH, EMPTY_POSITION, MAN_VS_MAN_PACKET, MAN_VS_AI_PACKET, \
    AI_VS_AI_PACKET, ACK_PACKET, RESET_PACKET, DUMMY_PACKET


class Game:
    def __init__(self, com_port: str) -> None:
        self._bleak_thread_ = None
        self._channel_ = Channel(com_port)

        self._screen_ = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._clock_ = pygame.time.Clock()

        self._cells_ = [pygame.FRect((0, 0), (0, 0)) for _ in range(CELLS_NUMBER ** 2)]

        self._figures_to_display_: list[tuple[tuple[int, int], str], ...] = [EMPTY_POSITION for _ in
                                                                             range(CELLS_NUMBER ** 2)]
        self._figures_ = [0xFF for _ in range(CELLS_NUMBER ** 2)]

        self._figure_names_ = ["cross", "nod"]
        self._current_figure_ = 0

        self._font_ = pygame.font.SysFont("Arial", 24)

        self._mvm_rect_ = pygame.FRect((SCREEN_WIDTH // 10, SCREEN_HEIGHT // 1.25),
                                       (SCREEN_WIDTH // 1.25, SCREEN_HEIGHT // 8))
        self._mva_rect_ = pygame.FRect((SCREEN_WIDTH // 10, SCREEN_HEIGHT // 2.25),
                                       (SCREEN_WIDTH // 1.25, SCREEN_HEIGHT // 8))
        self._ava_rect_ = pygame.FRect((SCREEN_WIDTH // 10, SCREEN_HEIGHT // 8),
                                       (SCREEN_WIDTH // 1.25, SCREEN_HEIGHT // 8))

        self._game_running_ = True
        self._game_packet_send_ = False

        self._click_delay_ = 0
        self._counter_ = 0

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
            self._channel_.send_message(MAN_VS_MAN_PACKET)
        elif self._mva_rect_.collidepoint(mouse_position):
            self._game_type_ = 2
            self._channel_.send_message(MAN_VS_AI_PACKET)
        elif self._ava_rect_.collidepoint(mouse_position):
            self._game_type_ = 3
            self._channel_.send_message(AI_VS_AI_PACKET)

    def place_figure(self, packet: bytes) -> None:
        figures = [int(value) for value in packet]

        if self._figures_ == figures:
            return

        self._figures_ = figures

        try:
            self._figures_to_display_ = [((i // CELLS_NUMBER, i % CELLS_NUMBER), self._figure_names_[value])
                                         if value != 0xFF else EMPTY_POSITION
                                         for i, value in enumerate(self._figures_)]
        except Exception as error:  # noqa
            ...

    def check_win(self, packet: bytes) -> None:
        if b"\x88" in packet:
            self._game_running_ = False
            self._winner_ = "cross"
        elif b"\x77" in packet:
            self._game_running_ = False
            self._winner_ = "nod"
        elif b"\x22" in packet:
            self._game_running_ = False
            self._winner_ = "tie"

    def run(self) -> None:
        self.fill_board()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP and not self._click_delay_:
                    print("Click")

                    if self._game_type_ == 0:
                        self.check_menu()
                    else:
                        x, y = pygame.mouse.get_pos()

                        figure_index_x = x * CELLS_NUMBER // SCREEN_WIDTH + 1
                        figure_index_y = y * CELLS_NUMBER // SCREEN_HEIGHT + 1

                        self._channel_.send_message(bytes([figure_index_x, figure_index_y]))

                    self._click_delay_ = FPS // 3
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        print("Reset Sent")

                        self._channel_.send_message(RESET_PACKET)
                        self._game_type_ = 0

            packet = self._channel_.receive_message()

            match self._game_type_:
                case 0:
                    self.draw_menu()
                case 1:
                    self.draw_board()
                    self.draw_figures()
                    self.check_win(packet)
                case 2:
                    self.draw_board()
                    self.draw_figures()
                    self.check_win(packet)
                case 3:
                    self.draw_board()
                    self.draw_figures()
                    self.check_win(packet)

            if not self._game_running_:
                break

            if (packet and packet != ACK_PACKET
                    and packet != DUMMY_PACKET
                    and len(packet) == CELLS_NUMBER ** 2):
                self.place_figure(packet)

            if self._game_type_ != 0:
                self._channel_.send_message(DUMMY_PACKET)

                self._counter_ = 0

            if self._click_delay_:
                self._click_delay_ -= 1

            self._clock_.tick(FPS)
            pygame.display.update()

        print(f"Winner: {self._winner_}")

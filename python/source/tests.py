import unittest
import pygame

from source.constants import CELLS_NUMBER, LIGHT_COLOR
from source.game import Game


class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_init(self):
        self.assertIsNone(self.game._bleak_thread_)
        self.assertIsNotNone(self.game._channel_)
        self.assertIsNotNone(self.game._screen_)
        self.assertIsNotNone(self.game._clock_)
        self.assertIsNotNone(self.game._cells_)
        self.assertIsNotNone(self.game._figures_)
        self.assertIsNotNone(self.game._font_)

    def test_fill_board(self):
        self.game.fill_board()
        self.assertEqual(len(self.game._cells_), CELLS_NUMBER ** 2)

    def test_draw_board(self):
        self.game.draw_board()
        self.game._screen_.fill(LIGHT_COLOR)
        pygame.display.update()

    def test_draw_figure(self):
        self.game.draw_figure((0, 0), "cross")
        self.game._screen_.fill(LIGHT_COLOR)
        pygame.display.update()

    def test_draw_figures(self):
        self.game.draw_figures()
        self.game._screen_.fill(LIGHT_COLOR)
        pygame.display.update()

    def test_draw_menu(self):
        self.game.draw_menu()
        self.game._screen_.fill(LIGHT_COLOR)
        pygame.display.update()

    def test_check_menu(self):
        self.game.check_menu()
        self.assertEqual(self.game._game_type_, 0)

    def test_place_figure(self):
        packet = bytes([0x01, 0x02, 0x03])
        self.game.place_figure(packet)
        self.assertEqual(self.game._figures_, [0x01, 0x02, 0x03])

    def test_check_win(self):
        packet = bytes([0x88])
        self.game.check_win(packet)
        self.assertFalse(self.game._game_running_)
        self.assertEqual(self.game._winner_, "cross")

    def test_run(self):
        self.game.run()
        self.assertFalse(self.game._game_running_)


if __name__ == "__main__":
    unittest.main()

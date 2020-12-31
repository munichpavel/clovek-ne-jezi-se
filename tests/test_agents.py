"""Tests for clovek_ne_jezi_se.agents"""
from clovek_ne_jezi_se.client import Client
from clovek_ne_jezi_se.agents import HumanPlayer
from clovek_ne_jezi_se.game_state import EMPTY_SYMBOL


class TestHumanPlayer:
    player_names = ['red', 'blue', 'green', 'yellow']
    players = [HumanPlayer(name=name) for name in player_names]

    client = Client(players=players)
    client.initialize()
    game_state = client.get_game_state()

    def test_get_waiting_area_representation(self):
        res = self.players[0].get_waiting_area_representation(self.game_state)

        assert res == dict(red=4, blue=4, green=4, yellow=4)

    def test_get_main_spaces_as_list(self):
        res = self.players[0].get_main_spaces_representation(self.game_state)
        expected = self.game_state.section_length \
            * len(self.game_state.player_names) \
            * [EMPTY_SYMBOL]

        assert res == expected

    def test_get_home_area_representation(self):
        res = self.players[0].get_home_area_representation(self.game_state)

        assert res == dict(red=0, blue=0, green=0, yellow=0)

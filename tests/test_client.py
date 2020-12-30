"""Tests for clovek_ne_jezi_se.Client"""
from clovek_ne_jezi_se.client import Client
from clovek_ne_jezi_se.agent import Player
from clovek_ne_jezi_se.game_state import GameState


def monkey_roll(roll_value):
    """Monkeypatch for dice roll"""
    return roll_value


class TestClient:
    player_names = ['red', 'blue', 'green', 'yellow']
    players = [Player(name=name) for name in player_names]

    client = Client(players=players)
    client.initialize()

    def test_initial_state(self):
        expected_game_state = GameState(self.player_names)

        assert self.client.get_game_state() == expected_game_state

    def test_next_player(self):
        player_round = [
            self.client.next_player() for _ in range(len(self.player_names))
        ]

        assert player_round == self.players

    def test_dice_roll_monkeypatch(self, monkeypatch):
        value = 1
        monkeypatch.setattr(self.client, 'roll', lambda: monkey_roll(value))
        assert self.client.roll() == value

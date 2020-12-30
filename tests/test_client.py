"""Tests for clovek_ne_jezi_se.Client"""
from clovek_ne_jezi_se.client import Client
from clovek_ne_jezi_se.agent import Player
from clovek_ne_jezi_se.game_state import GameState


def test_initial_state():
    player_names = ['red', 'blue', 'green', 'yellow']
    players = [Player(name=name) for name in player_names]

    client = Client(players=players, main_board_section_length=4)
    client.initialize()

    expected_game_state = GameState(player_names, section_length=4)

    assert client.get_game_state() == expected_game_state


def test_next_player():
    player_names = ['red', 'blue', 'green', 'yellow']
    players = [Player(name=name) for name in player_names]

    client = Client(players=players)
    client.initialize()
    player_round = [
        client.next_player() for _ in range(len(player_names))
    ]

    assert player_round == players


def monkey_roll(roll_value):
    return roll_value


def test_dice_roll_monkeypatch(monkeypatch):
    player_names = ['red', 'blue', 'green', 'yellow']
    players = [Player(name=name) for name in player_names]

    client = Client(players=players, number_of_dice_faces=6)
    client.initialize()
    value = 1
    monkeypatch.setattr(client, 'roll', lambda: monkey_roll(value))
    assert client.roll() == value



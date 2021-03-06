"""Tests for running experiments"""
import json
import pytest

from clovek_ne_jezi_se.run_experiments import parse_config_file, initialize_client

def test_parse_config_file(tmpdir):
    config = '''{
  "players": [
    {
      "name": "red",
      "agent": "FurthestAlongPlayer",
      "kwargs": {
        "print_game_state": false
      }
    }
  ],
  "board": {
    "main_board_section_length": 4,
    "pieces_per_player": 4,
    "number_of_dice_faces": 6
  },
  "n_runs": 1
}
'''

    expected = dict(
        players=[
            dict(
                name='red', agent='FurthestAlongPlayer',
                kwargs=dict(print_game_state=False)
            )
        ],
        board=dict(
            main_board_section_length=4,
            pieces_per_player=4,
            number_of_dice_faces=6
        ),
        n_runs=1
    )
    tmp_file = tmpdir / 'config.json'
    with open(tmp_file, 'w') as fp:
        fp.write(config)

    res = parse_config_file(tmp_file)
    assert res == expected


@pytest.mark.parametrize(
    'config,is_valid,Error',
    [
        (dict(players=[
            dict(name='red', agent='FurthestAlongPlayer',
                 kwargs=dict(print_game_state=False))
            ],
            board=dict(main_board_section_length=4, pieces_per_player=4,
                       number_of_dice_faces=6),
            n_runs=1
        ), True, None),
        (dict(
            board=dict(main_board_section_length=4, pieces_per_player=4,
                       number_of_dice_faces=6),
            n_runs=1
        ), False, KeyError),
        (dict(players=[
            dict(name='red', agent='FurthestAlongPlayer',
                 kwargs=dict(print_game_state=False))
            ],
            board=dict(),  # All board values must be given
            n_runs=1
        ), False, TypeError),
    ]
)
def test_initialize_client(config, is_valid, Error):
    if is_valid:
        initialize_client(config)
    else:
        with pytest.raises(Error):
            initialize_client(config)
"""Tests for running experiments"""
import json
import pytest

from clovek_ne_jezi_se.run_experiments import parse_config_file

def test_parse_config_file(tmpdir):
    config = '''{
  "players": [
    {
      "name": "red",
      "agent": "FurthestAlongPlayer",
      "kwargs": {
        "print_to_screen": false
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
                kwargs=dict(print_to_screen=False)
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
    print(type(res))
    assert res == expected
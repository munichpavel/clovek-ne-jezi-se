"""Tests for running experiments"""
import json
import pytest

from clovek_ne_jezi_se.run_experiments import (
    parse_config_file, initialize_client, get_experiment_variables_from_config_dir
)

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
    tmp_path = tmpdir / 'config.json'
    with open(tmp_path, 'w') as fp:
        fp.write(config)

    res = parse_config_file(tmp_path)
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


valid_config = '''{
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
invalid_game_config = '''{
  "players": [
    {
      "name": "red",
      "agent": "FurthestAlongPlayer",
      "kwargs": {
        "print_game_state": false
      }
    }
  ],
  "n_runs": 1
}
'''
invalid_n_runs_config = '''{
  "players": [
    {
      "name": "red",
      "agent": "FurthestAlongPlayer",
      "kwargs": {
        "print_game_state": false
      }
    }
  ]
}
'''

@pytest.mark.parametrize(
    'configs,is_valid,Error',
    [
        ([valid_config, valid_config], True, None),
        ([valid_config, invalid_game_config], False, KeyError),
        ([valid_config, invalid_n_runs_config], False, KeyError)
    ]
)
def test_get_clients_from_configs_validation(tmpdir, configs, is_valid, Error):
    for idx, config in enumerate(configs):
        tmp_path = tmpdir / (str(idx) + '.json')
        with open(tmp_path, 'w') as fp:
            fp.write(config)

    if is_valid:
        get_experiment_variables_from_config_dir(tmpdir)
    else:
        with pytest.raises(Error):
            get_experiment_variables_from_config_dir(tmpdir)

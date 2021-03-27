from typing import Sequence
import json
from copy import deepcopy

from pathlib import Path

import click
import mlflow

from clovek_ne_jezi_se.client import Client
from clovek_ne_jezi_se.agents import RandomPlayer, FurthestAlongPlayer


@click.command()
@click.option('--config_dir', help='Directory holding experiment configurations')
def run_experiments(config_dir):

    config_dir = Path(config_dir)
    click.echo(f'Getting experiment variables from {config_dir}')
    experiment_group_variables = get_experiment_variables_from_config_dir(config_dir)

    experiment_group_name = config_dir.name
    mlflow.set_experiment(experiment_group_name)
    click.echo(f'Running experiments {experiment_group_name}')
    for experiment_variables in experiment_group_variables:

        n_runs = experiment_variables['n_runs']
        for idx in range(n_runs):
            click.echo(f'Running experiment {idx} of {n_runs}')
            with mlflow.start_run():
                client = deepcopy(experiment_variables['client'])
                agent_names = [player.__class__.__name__ for player in client.players]
                run_dict = dict(
                    agents=','.join(agent_names),
                    main_board_section_length=client.main_board_section_length,
                    pieces_per_player=client.pieces_per_player,
                    number_of_dice_faces=client.number_of_dice_faces
                )

                mlflow.log_params(run_dict)

                winner, n_plays = client.play()

                winner_idx = client.players.index(winner)
                print(f'Winner of round is {winner}')
                mlflow.log_metric('winner_idx', winner_idx)
                mlflow.log_metric('n_plays', n_plays)

def get_experiment_variables_from_config_dir(config_dir) -> Sequence[dict]:
    """Get experiment variables from files in config_dir"""
    res = []
    if not isinstance(config_dir, Path):
        config_dir = Path(config_dir)
    for fp in config_dir.iterdir():
        config = parse_config_file(fp)
        client = initialize_client(config)
        n_runs = config['n_runs']
        res.append(dict(client=client, n_runs=n_runs))

    return res

def parse_config_file(config_path: Path) -> dict:
    """Return experiment configuration dictionary from file content"""
    with open(config_path, 'r') as fp:
        config = json.load(fp)
    return config


def initialize_client(config: dict) -> 'Client':

    players = [
        eval(player['agent'])(name=player['name'], **player['kwargs'])
        for player in config['players']
    ]

    client = Client(players=players, **config['board'])
    client.initialize()
    return client

if __name__ == '__main__':
    run_experiments()

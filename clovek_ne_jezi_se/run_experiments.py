from pathlib import Path
import json

import click
import mlflow

from clovek_ne_jezi_se.client import Client
from clovek_ne_jezi_se.agents import RandomPlayer, FurthestAlongPlayer


@click.command()
@click.option('--config_dir', help='Directory holding experiment configurations')
def run_experiments(config_dir):
    click.echo(f'Running experiments from {config_dir}')

def parse_config_file(config_path: Path) -> dict:
    """Return experiment configuration dictionary from file content"""
    with open(config_path, 'r') as fp:
        config = json.load(fp)
    return config

if __name__ == '__main__':
    run_experiments()

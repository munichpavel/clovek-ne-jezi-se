import logging
import os
from datetime import datetime
from pathlib import Path


from clovek_ne_jezi_se.client import Client
from clovek_ne_jezi_se.agents import HumanPlayer, RandomPlayer

log_dir = Path(os.environ['LOG_DIR'])
file_name = datetime.now().strftime('experiment-%Y-%m-%d-%H:%M.%S.log')
logging.basicConfig(filename=log_dir / file_name, level=logging.INFO)


player_names = ['red', 'blue']#, 'green', 'yellow']

random_players = [
    RandomPlayer(name=name, print_game_state=False) for name in player_names
]

n_experiments = 10
for _ in range(n_experiments):
    client = Client(
        players=random_players,
        main_board_section_length=1
    )
    client.initialize()
    logging.info(client)

    winner, n_plays = client.play()
    logging.info(f'Winner: {winner}')
    logging.info(f'Number of turns: {n_plays}')

import mlflow
from mlflow.tracking import MlflowClient


from clovek_ne_jezi_se.client import Client
from clovek_ne_jezi_se.agents import HumanPlayer, RandomPlayer

player_names = ['red', 'blue', 'green', 'yellow']

random_players = [
    RandomPlayer(name=name, print_game_state=False) for name in player_names
]

players = random_players


n_runs = 99
main_board_section_length = 1
pieces_per_player = 4
number_of_dice_faces = 6
agents = [player.__class__.__name__ for player in players]

run_dict = dict(
    agents=str(agents),
    main_board_section_length=main_board_section_length,
    pieces_per_player=pieces_per_player,
    number_of_dice_faces=number_of_dice_faces
)


for _ in range(n_runs):
    with mlflow.start_run():
        mlflow.log_params(run_dict)

        client = Client(
            players=players,
            main_board_section_length=main_board_section_length,
            pieces_per_player=pieces_per_player,
            number_of_dice_faces=number_of_dice_faces
        )
        client.initialize()

        winner, n_plays = client.play()

        winner_idx = players.index(winner)
        print(f'Winner of round is {winner}')
        mlflow.log_metric('winner_idx', winner_idx)
        mlflow.log_metric('n_plays', n_plays)

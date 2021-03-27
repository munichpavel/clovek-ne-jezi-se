# clovek-ne-jezi-se

Work-in-progress implementation of Clovek Ne Jezi Se (Slovenian) / [Mensch Ärgere Dich Nicht](https://de.wikipedia.org/wiki/Mensch_%C3%A4rgere_Dich_nicht) (German) for reinforcement learning experimentation.

See the [demo notebook](notebooks/demo.ipynb) for features and example usage.

## Experiments

Exeriments can be run via configuration json files.

For creating experiment configurations, see the [notebooks/generate-experiment-configs-example.ipynb](notebooks/generate-experiment-configs-example.ipynb).

To run the experiments created in the above notebook, run

```console
 python clovek_ne_jezi_se/run_experiments.py \
   --config_dir=$EXPERIMENT_CONFIGS_DIR/player-order
```

## Development

See the [installation guide](docs/source/INSTALL.rst) for instructions on local development.

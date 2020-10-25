'''Utility functions'''

from typing import Sequence
from math import pi

import numpy as np
import networkx as nx


def make_even_points_on_circle(
    center: Sequence, radius: float, n_points: int,
    start_radians=0, clockwise=True
) -> np.array:
    """"""
    if clockwise:
        endpoint_sign = -1
    else:
        endpoint_sign = 1

    radians = [
        idx for idx in np.linspace(
            start_radians, endpoint_sign * 2 * pi + start_radians,
            num=n_points, endpoint=False
        )
    ]
    res = []
    for radian in radians:
        x = center[0] + radius * np.cos(radian)
        y = center[1] + radius * np.sin(radian)
        point = np.array([x, y])
        res.append(point)

    return np.array(res)


def make_dict_from_lists(key_list: list, value_list: list) -> dict:
    return dict(zip(key_list, value_list))


def get_node_filtered_subgraph(graph, query_dict: dict) -> nx.DiGraph:
    def filter_node(node_name):
        res = []
        for key, value in query_dict.items():
            res.append(graph.nodes[node_name].get(key) == value)
        return np.all(res)

    return nx.subgraph_view(graph, filter_node=filter_node)

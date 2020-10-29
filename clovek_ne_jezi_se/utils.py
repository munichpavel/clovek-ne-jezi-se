'''Utility functions'''

from typing import Sequence
from math import pi

import numpy as np
import attr

import networkx as nx
import networkx.algorithms.isomorphism as iso


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


def is_label_isomorphic(
    graph, other, graph_label_matchers: list
) -> bool:
    pass


def is_label_matched(
    graph, other, graph_label_matcher
) -> bool:
    """
    Returns True if and only if graphs are isomorphic and all labeled values
    are identical.

    """
    if graph_label_matcher.match_type == 'node':
        return iso.is_isomorphic(
            graph, other,
            node_match=graph_label_matcher.get_match_function()
        )
    elif graph_label_matcher.match_type == 'edge':
        return iso.is_isomorphic(
            graph, other,
            edge_match=graph_label_matcher.get_match_function()
        )


@attr.s
class GraphLabelMatcher:
    match_type = attr.ib(type=str)
    value_type = attr.ib(type=str)
    labels = attr.ib(type=list)

    @match_type.validator
    def check_match_type(self, attribute, value):
        allowed_values = ['node', 'edge']
        if value not in allowed_values:
            raise ValueError(f'match_type must be in {allowed_values}')

    @value_type.validator
    def check_value_type(self, attribute, value):
        allowed_values = ['numerical', 'categorical']
        if value not in allowed_values:
            raise ValueError(f'value_type must be in {allowed_values}')

    def get_match_function(self):
        return self._matcher_factory(self.match_type, self.value_type)

    def _matcher_factory(self, match_type, value_type):
        factory_dict = dict(node=dict(), edge=dict())

        # TODO Is this dangerous?
        numerical_default = 0.
        categorical_default = None
        factory_dict['node']['categorical'] = iso.categorical_node_match(
            self.labels, len(self.labels) * [categorical_default]
        )
        factory_dict['node']['numerical'] = iso.numerical_node_match(
            self.labels, len(self.labels) * [numerical_default]
        )
        factory_dict['edge']['categorical'] = iso.categorical_edge_match(
            self.labels, len(self.labels) * [categorical_default]
        )
        factory_dict['edge']['numerical'] = iso.numerical_edge_match(
            self.labels, len(self.labels) * [numerical_default]
        )

        return factory_dict[match_type][value_type]


def get_node_filtered_subgraph(graph, query_dict: dict) -> nx.DiGraph:
    def filter_node(node_name):
        res = []
        for key, value in query_dict.items():
            res.append(graph.nodes[node_name].get(key) == value)
        return np.all(res)

    return nx.subgraph_view(graph, filter_node=filter_node)

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
    """
    Returns True if and only if graphs are isomorphic and specified labels
    in all of the graph_label_matchers are identical for the two graphs.

    Wrapper around is_label_matched.

    Parameters
    ----------
    graph : networkx.graph
    other : networks.graph
    graph_label_matcher : list
        List of GraphLabelMatcher's
    """
    res = []
    res.append(iso.is_isomorphic(graph, other))
    for matcher in graph_label_matchers:
        res.append(is_label_matched(graph, other, matcher))
    return np.all(res)


def is_label_matched(
    graph, other, graph_label_matcher: "GraphLabelMatcher"
) -> bool:
    """
    Returns True if and only if graphs are isomorphic and specified labels
    in graph_label_matcher are identical.

    Parameters
    ----------
    graph : networkx.Graph
    other : networkx.Graph
    graph_label_matcher : GraphLabelMatcher
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
    """
    Specification of graph annotation matching method for labeled graphs
    to be considered equal. The matching methods are from
    `networkx.algorithms.isomorphism`.


    Parameters
    ----------
    match_type : str
        One of 'node', 'edge'
    value_type : str
        One of 'numerical', 'categorical'
    labels : list
        The edge or node label values for which to check equality
    """
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


def get_node_filtered_subgraph(graph: nx.Graph, query_dict: dict) -> nx.Graph:
    """
    Return a subgraph of input graph according to node values specified in
    the query_dict.

    Parameters
    ----------
    graph : nx.Graph
    query_dict : dict
        Dict of form {<node_label_name>: node_label_value}
    """
    def filter_node(node_name):
        res = []
        for key, value in query_dict.items():
            res.append(graph.nodes[node_name].get(key) == value)
        return np.all(res)

    return nx.subgraph_view(graph, filter_node=filter_node)


def get_node_filtered_node_names(graph: nx.Graph, query_dict: dict) -> list:
    """Return a list of node names from the subgraph query"""
    subgraph = get_node_filtered_subgraph(graph, query_dict)
    res = list(subgraph.nodes)
    return res


def get_edge_filtered_subgraph(
    graph, query_dict: dict, query_type: str
) -> nx.DiGraph:
    """
    Return a subgraph of input graph according to edge values specified in
    the query_dict. Nodes of degree 0 after filtering are removed.

    Parameters
    ----------
    graph : nx.Graph
    query_dict : dict
        Dict of form {<edge_label_name>: edge_label_value}
    query_type : str
        Dictates whether filtering is by value equality or inclusion
    """
    def filter_edge_by_equality(node_start, node_stop):
        res = []
        for key, value in query_dict.items():
            res.append(graph[node_start][node_stop].get(key) == value)
        return np.all(res)

    def filter_edge_by_inclusion(node_start, node_stop):
        res = []
        for key, value in query_dict.items():
            res.append(value in graph[node_start][node_stop].get(key, []))
        return np.all(res)

    if query_type == 'equality':
        filter_edge = filter_edge_by_equality
    elif query_type == 'inclusion':
        filter_edge = filter_edge_by_inclusion

    res = nx.subgraph_view(graph, filter_edge=filter_edge)
    # Keep only nodes of degree > 0 after edge filtering
    subgraph_node_names = []
    for node_name in res.nodes:
        if nx.degree(res, node_name) > 0:
            subgraph_node_names.append(node_name)
    res = nx.subgraph(res, subgraph_node_names)
    return res

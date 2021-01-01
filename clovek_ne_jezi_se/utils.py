'''Utility functions'''

from typing import Sequence, Union
from math import pi
from numbers import Number
from copy import deepcopy

import numpy as np
import attr

import networkx as nx
import networkx.algorithms.isomorphism as iso


def make_even_points_on_circle(
    center: Sequence, radius: float, n_points: int,
    start_radians: float = 0, clockwise: bool = True
) -> np.array:
    """
    Generate evenly spaces points on a circle.

    Parameters
    ----------
    center :
        2-tuple of coordinates in R2 for center
    radius :
        Radius of circle
    n_points :
        Number of points to be distributed on circle
    start_radians :
        Angle in radians for initial points placement
    clockwise :
        Placement order of points, clockwise or counter-clockwise
    """
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
    """Return dict with given keys and values."""
    return dict(zip(key_list, value_list))


def is_label_isomorphic(
    graph: nx.Graph, other: nx.Graph,
    graph_query_paramses: Sequence["GraphQueryParams"]
) -> bool:
    """
    Returns True if and only if graphs are isomorphic and specified labels
    in all of the graph_label_matchers are identical for the two graphs.

    Wrapper around is_label_matched.

    Parameters
    ----------
    graph :
    other :
    graph_query_paramses :
        List of GraphQueryParam's
    """
    res = []
    res.append(iso.is_isomorphic(graph, other))
    for query_params in graph_query_paramses:
        res.append(_is_single_label_isomorphic(graph, other, query_params))
    return np.all(res)


def _is_single_label_isomorphic(
    graph: nx.Graph, other: nx.Graph, graph_query_params: "GraphQueryParams"
) -> bool:
    """
    Returns True if and only if graphs are isomorphic and specified label
    in graph_query_params are identical.
    """
    if graph_query_params.graph_component == 'node':
        return iso.is_isomorphic(
            graph, other,
            node_match=graph_query_params.get_match_function()
        )
    elif graph_query_params.graph_component == 'edge':
        return iso.is_isomorphic(
            graph, other,
            edge_match=graph_query_params.get_match_function()
        )


@attr.s
class GraphQueryParams:
    """Container for doing graph filtering"""
    graph_component = attr.ib(
        type=str,
        validator=attr.validators.in_(['node', 'edge'])
    )
    label = attr.ib(type=str)
    query_type = attr.ib(
        type=Union[str, None], default=None,
        validator=attr.validators.in_(['equality', 'inclusion', None])
    )
    value = attr.ib(type=Union[str, int, float, None], default=None)
    value_type = attr.ib(type=Union[str, None], default=None)

    def set_value_type(self):
        """Impute value_type based on value."""
        if isinstance(self.value, str):
            self.value_type = 'categorical'
        elif isinstance(self.value, Number):
            self.value_type = 'numerical'
        else:
            raise TypeError(
                f'value {self.value} is neither {str} nor {Number}'
            )

    def get_match_function(self):
        """Return matching function for instance"""
        return self._matcher_factory(self.graph_component, self.value_type)

    def _matcher_factory(self, graph_component, value_type):
        factory_dict = dict(node=dict(), edge=dict())

        # TODO Is this dangerous?
        numerical_default = 0.
        categorical_default = None

        factory_dict['node']['categorical'] = iso.categorical_node_match(
            self.label, categorical_default
        )
        factory_dict['node']['numerical'] = iso.numerical_node_match(
            self.label, numerical_default
        )
        factory_dict['edge']['categorical'] = iso.categorical_edge_match(
            self.label, categorical_default
        )
        factory_dict['edge']['numerical'] = iso.numerical_edge_match(
            self.label, numerical_default
        )

        return factory_dict[graph_component][value_type]


def get_filtered_subgraph_view(
    graph: nx.Graph, query_paramses: Sequence["GraphQueryParams"]
) -> nx.Graph:
    """
    Return a subgraph view of the input graph that satisifies all queries
    specified in the query_paramses list.
    """
    res = deepcopy(graph)
    for query_params in query_paramses:
        res = _get_single_filtered_subgraph(res, query_params)

    return res


def _get_single_filtered_subgraph(
    graph: nx.Graph, query_params: "GraphQueryParams"
) -> nx.Graph:
    """
    Return a subgraph of input graph according to the query specified in the
    input GraphQueryParams.
    """
    if query_params.graph_component == 'node':
        return get_node_filtered_subgraph_view(graph, query_params)

    elif query_params.graph_component == 'edge':
        return get_edge_filtered_subgraph_view(graph, query_params)


def get_node_filtered_subgraph_view(
    graph: nx.Graph, query_params: "GraphQueryParams"
) -> nx.Graph:
    """
    Return a subgraph view of input graph according to node values specified in
    the query_dict.
    """
    def filter_node_by_equality(node_name):
        res = graph.nodes[node_name].get(query_params.label) \
            == query_params.value
        return res

    def filter_node_by_inclusion(node_name):
        res = query_params.value in \
            graph.nodes[node_name].get(query_params.label, [])
        return res

    if query_params.query_type == 'equality':
        filter_node = filter_node_by_equality
    elif query_params.query_type == 'inclusion':
        filter_node = filter_node_by_inclusion

    return nx.subgraph_view(graph, filter_node=filter_node)


def get_edge_filtered_subgraph_view(
    graph: nx.Graph, query_params: "GraphQueryParams"
) -> nx.Graph:
    """
    Return a subgraph view of input graph according to edge values specified in
    the query_dict. Nodes of degree 0 after filtering are removed.
    """
    def filter_edge_by_equality(node_start, node_stop):
        res = graph[node_start][node_stop].get(query_params.label) \
            == query_params.value
        return res

    def filter_edge_by_inclusion(node_start, node_stop):
        res = query_params.value in \
            graph[node_start][node_stop].get(query_params.label, [])
        return res

    if query_params.query_type == 'equality':
        filter_edge = filter_edge_by_equality

    elif query_params.query_type == 'inclusion':
        filter_edge = filter_edge_by_inclusion

    res = nx.subgraph_view(graph, filter_edge=filter_edge)

    # Keep only nodes of degree > 0 after edge filtering
    subgraph_node_names = []
    for node_name in res.nodes:
        if nx.degree(res, node_name) > 0:
            subgraph_node_names.append(node_name)
    res = nx.subgraph(res, subgraph_node_names)
    return res


def get_filtered_node_names(
    graph: nx.Graph, query_paramses: Sequence["GraphQueryParams"]
) -> list:
    """
    Return a list of node names from the subgraph query.
    """
    subgraph = get_filtered_subgraph_view(graph, query_paramses)
    res = list(subgraph.nodes)
    return res


def get_node_attribute_mapped_list(
    graph: nx.Graph, attribute, map: dict
) -> list:
    """
    Create list of mapped node attributes, e.g. for creating plots of graphs
    with colored nodes.
    """
    res = []
    for node_name in graph.nodes:
        attribute_value = graph.nodes[node_name][attribute]
        res.append(map[attribute_value])

    return res

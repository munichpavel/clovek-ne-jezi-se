from math import sqrt, pi
from copy import deepcopy

import pytest

import numpy as np

import networkx as nx

from clovek_ne_jezi_se.utils import (
    make_even_points_on_circle, make_dict_from_lists,
    is_labeled_isomorphic, get_node_filtered_subgraph
)


@pytest.mark.parametrize(
    'center,radius,n_points,start_radians,clockwise,expected',
    [
        (
            (0, 0), 1, 3, 0, True,
            np.array([
                np.array([1., 0.]),
                np.array([-1. / 2, -sqrt(3) / 2]),
                np.array([-1. / 2, sqrt(3) / 2])
            ])
        ),
        (
            (0, 0), 1, 4, 0, True,
            np.array([
                np.array([1., 0.]),
                np.array([0., -1.]),
                np.array([-1., 0.]),
                np.array([0., 1.])
            ])
        ),
        (
            (0, 0), 1, 3, 0, False,
            np.array([
                np.array([1., 0.]),
                np.array([-1. / 2, sqrt(3) / 2]),
                np.array([-1. / 2, -sqrt(3) / 2])
            ])
        ),
        (
            (0, 0), 1, 3, pi, False,
            np.array([
                np.array([-1., 0.]),
                np.array([1. / 2, -sqrt(3) / 2]),
                np.array([1. / 2, sqrt(3) / 2])
            ])
        )
    ]
)
def test_make_even_points_on_circle(
    center, radius, n_points, start_radians, clockwise, expected
):
    points = make_even_points_on_circle(
        center=center, radius=radius, n_points=n_points,
        start_radians=start_radians, clockwise=clockwise
    )
    np.testing.assert_array_almost_equal(points, expected)


def test_make_dict_from_lists():
    key_list = ['key1', 'key2']
    value_list = ['v1', 'v2']

    expected = dict(key1='v1', key2='v2')
    assert make_dict_from_lists(key_list, value_list) == expected


# Define test graphs
two_cycle_digraph = nx.cycle_graph(2, create_using=nx.DiGraph)

labeled_two_cycle_digraph = deepcopy(two_cycle_digraph)
# Assign node label values
labeled_two_cycle_digraph.nodes[0]['descriptor'] = 'schlamazel'
labeled_two_cycle_digraph.nodes[1]['descriptor'] = 'yutz'
# Assign edge label value
labeled_two_cycle_digraph[0][1]['color'] = 'orange'

var_labeled_two_cycle_digraph = deepcopy(labeled_two_cycle_digraph)
# Add node label value
var_labeled_two_cycle_digraph.nodes[0]['sign'] = 'pisces'
# Add edge label value
var_labeled_two_cycle_digraph[0][1]['mood'] = 'happy'


@pytest.mark.parametrize(
    'graph,other,kwarg_dict,expected',
    [
        (two_cycle_digraph, two_cycle_digraph, {}, True),
        (
            two_cycle_digraph, labeled_two_cycle_digraph,
            dict(categorical_node_labels=['descriptor']),
            False
        ),
        (
            labeled_two_cycle_digraph, labeled_two_cycle_digraph,
            dict(categorical_node_labels=['descriptor']),
            True
        ),
        (
            labeled_two_cycle_digraph, var_labeled_two_cycle_digraph,
            dict(categorical_node_labels=['descriptor']),
            True
        ),
        (
            labeled_two_cycle_digraph, var_labeled_two_cycle_digraph,
            dict(categorical_node_labels=['descriptor', 'sign']),
            False
        ),
        (
            labeled_two_cycle_digraph, labeled_two_cycle_digraph,
            dict(categorical_edge_labels=['color']),
            True
        ),
        (
            labeled_two_cycle_digraph, var_labeled_two_cycle_digraph,
            dict(categorical_edge_labels=['color']),
            True
        ),
        (
            labeled_two_cycle_digraph, var_labeled_two_cycle_digraph,
            dict(categorical_edge_labels=['color', 'mood']),
            False
        )
    ]
)
def test_is_labeled_isomorphic(graph, other, kwarg_dict, expected):

    assert is_labeled_isomorphic(graph, other, **kwarg_dict) == expected


# def test_get_node_filtered_subgraph():
#     g = nx.cycle_graph(3, create_using=nx.DiGraph)
#     descriptors = ['schlamazel', 'yutz', 'yutz']
#     for node_name, descriptor in zip(g.nodes(), descriptors):
#         g.nodes[node_name]['descriptor'] = descriptor

#     expected = nx.DiGraph()
#     expected.add_nodes_from([1,2], descriptor='yutz')
#     expected.add_edge(1,2)

#     query_dict=dict(descriptor='yutz')
#     assert get_node_filtered_subgraph(g, query_dict) == expected

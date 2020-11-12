from math import sqrt, pi
from copy import deepcopy

import pytest

import numpy as np

import networkx as nx

from networkx.algorithms import isomorphism as iso

from clovek_ne_jezi_se.utils import (
    make_even_points_on_circle, make_dict_from_lists,
    GraphLabelMatcher,
    is_label_matched, is_label_isomorphic,
    get_node_filtered_subgraph, get_edge_filtered_subgraph
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


# Test GraphLabelMatcher
@pytest.mark.parametrize(
    'matcher_args',
    [
        (dict(match_type='duck', value_type='numerical', labels=['a_label'])),
        (dict(match_type='node', value_type='tubular', labels=['a_label'])),
    ]
)
def test_graph_label_matcher_errors(matcher_args):
    with pytest.raises(ValueError):
        GraphLabelMatcher(**matcher_args)


@pytest.mark.parametrize(
    'matcher,expected_match_function',
    [
        (
            GraphLabelMatcher(
                match_type='node', value_type='numerical',
                labels=['a_number']
            ),
            iso.numerical_node_match(['a_number'], [np.nan])
        ),
        (
            GraphLabelMatcher(
                match_type='node', value_type='categorical',
                labels=['a_category']
            ),
            iso.categorical_node_match(['a_category'], [None])
        ),
        (
            GraphLabelMatcher(
                match_type='edge', value_type='numerical',
                labels=['a_number']
            ),
            iso.numerical_edge_match(['a_number'], [np.nan])
        ),
        (
            GraphLabelMatcher(
                match_type='edge', value_type='categorical',
                labels=['a_category']
            ),
            iso.categorical_edge_match(['a_category'], [None])
        ),
    ]
)
def test_graph_label_matcher(matcher, expected_match_function):
    # Comparing byte code idea from
    # https://stackoverflow.com/questions/20059011/check-if-two-python-functions-are-equal
    assert matcher.get_match_function().__code__.co_code == \
        expected_match_function.__code__.co_code


# Define test graph fixtures
two_cycle_digraph = nx.cycle_graph(2, create_using=nx.DiGraph)

labeled_two_cycle_digraph = deepcopy(two_cycle_digraph)
# Assign node label values
labeled_two_cycle_digraph.nodes[0]['descriptor'] = 'schlamazel'
labeled_two_cycle_digraph.nodes[0]['trombone_count'] = 76
labeled_two_cycle_digraph.nodes[1]['descriptor'] = 'yutz'
labeled_two_cycle_digraph.nodes[1]['trombone_count'] = 42

# Assign edge label value
labeled_two_cycle_digraph[0][1]['color'] = 'orange'
labeled_two_cycle_digraph[0][1]['strength'] = 1

other_labeled_two_cycle_digraph = deepcopy(labeled_two_cycle_digraph)
# Add node label value
other_labeled_two_cycle_digraph.nodes[0]['sign'] = 'pisces'
other_labeled_two_cycle_digraph.nodes[0]['trombone_count'] = 0.
# Add edge label value
other_labeled_two_cycle_digraph[0][1]['mood'] = 'happy'
other_labeled_two_cycle_digraph[0][1]['strength'] = 3


@pytest.mark.parametrize(
    'graph,other,graph_label_matcher,expected',
    [
        (
            two_cycle_digraph, labeled_two_cycle_digraph,
            GraphLabelMatcher(
                match_type='node', value_type='categorical',
                labels=['descriptor']
            ),
            False
        ),
        (
            labeled_two_cycle_digraph, deepcopy(labeled_two_cycle_digraph),
            GraphLabelMatcher(
                match_type='node', value_type='categorical',
                labels=['descriptor']
            ),
            True
        ),
        (
            labeled_two_cycle_digraph, other_labeled_two_cycle_digraph,
            GraphLabelMatcher(
                match_type='node', value_type='categorical',
                labels=['descriptor']
            ),
            True
        ),
        (
            labeled_two_cycle_digraph, other_labeled_two_cycle_digraph,
            GraphLabelMatcher(
                match_type='node', value_type='categorical',
                labels=['descriptor', 'sign']
            ),
            False
        ),
        (
            labeled_two_cycle_digraph, labeled_two_cycle_digraph,
            GraphLabelMatcher(
                match_type='node', value_type='numerical',
                labels=['trombone_count']
            ),
            True
        ),
        (
            labeled_two_cycle_digraph, other_labeled_two_cycle_digraph,
            GraphLabelMatcher(
                match_type='node', value_type='numerical',
                labels=['trombone_count']
            ),
            False
        ),
        (
            labeled_two_cycle_digraph, labeled_two_cycle_digraph,
            GraphLabelMatcher(
                match_type='edge', value_type='categorical',
                labels=['color']
            ),
            True
        ),
        (
            labeled_two_cycle_digraph, other_labeled_two_cycle_digraph,
            GraphLabelMatcher(
                match_type='edge', value_type='categorical',
                labels=['color']
            ),
            True
        ),
        (
            labeled_two_cycle_digraph, other_labeled_two_cycle_digraph,
            GraphLabelMatcher(
                match_type='edge', value_type='categorical',
                labels=['color', 'mood']
            ),
            False
        ),
        (
            labeled_two_cycle_digraph, deepcopy(labeled_two_cycle_digraph),
            GraphLabelMatcher(
                match_type='edge', value_type='numerical',
                labels=['strength']
            ),
            True
        ),
        (
            labeled_two_cycle_digraph, other_labeled_two_cycle_digraph,
            GraphLabelMatcher(
                match_type='edge', value_type='numerical',
                labels=['strength']
            ),
            False
        ),

    ]
)
def test_is_label_matched(
    graph, other, graph_label_matcher, expected
):
    assert is_label_matched(graph, other, graph_label_matcher) \
        == expected


def test_is_label_isomorphic():
    assert is_label_isomorphic(
        labeled_two_cycle_digraph, other_labeled_two_cycle_digraph,
        graph_label_matchers=[
            GraphLabelMatcher(
                match_type='node', value_type='categorical',
                labels=['descriptor']
            ),
            GraphLabelMatcher(
                match_type='edge', value_type='categorical',
                labels=['color']
            ),
        ]
    )

    assert not is_label_isomorphic(
        labeled_two_cycle_digraph, other_labeled_two_cycle_digraph,
        graph_label_matchers=[
            GraphLabelMatcher(
                match_type='node', value_type='categorical',
                labels=['descriptor']
            ),
            GraphLabelMatcher(
                match_type='node', value_type='numerical',
                labels=['trombone_count']
            ),
            GraphLabelMatcher(
                match_type='edge', value_type='categorical',
                labels=['color']
            ),
        ]
    )


# Fixtures for graph filtering tests
pre_filter_graph = nx.cycle_graph(4, create_using=nx.DiGraph)
pre_filter_graph.nodes[0]['descriptor'] = 'schlamazel'
pre_filter_graph.nodes[1]['descriptor'] = 'yutz'
pre_filter_graph.nodes[2]['descriptor'] = 'yutz'
pre_filter_graph.nodes[3]['descriptor'] = 'yutz'

expected_filtered = nx.DiGraph()
expected_filtered.add_nodes_from([1, 2, 3], descriptor='yutz')
expected_filtered.add_edge(1, 2)
expected_filtered.add_edge(2, 3)


def test_get_node_filtered_subgraph():
    query_dict = dict(descriptor='yutz')
    res = get_node_filtered_subgraph(pre_filter_graph, query_dict)

    assert is_label_isomorphic(
        res, expected_filtered,
        graph_label_matchers=[
            GraphLabelMatcher(
                match_type='node', value_type='categorical',
                labels=['descriptor']
            ),
            GraphLabelMatcher(
                match_type='node', value_type='numerical',
                labels=['trombone_count']
            ),
        ]
    )

    assert not is_label_isomorphic(
        res, pre_filter_graph,
        graph_label_matchers=[
            GraphLabelMatcher(
                match_type='node', value_type='categorical',
                labels=['descriptor']
            ),
            GraphLabelMatcher(
                match_type='node', value_type='numerical',
                labels=['trombone_count']
            ),
        ]
    )


# For filtering by edge value equality
pre_filter_graph[0][1]['trombone_count'] = 0
pre_filter_graph[1][2]['trombone_count'] = 76
pre_filter_graph[2][3]['trombone_count'] = 76

# For filtering by edge value inclusion
pre_filter_graph[0][1]['allowed_instruments'] = ['trumpet']
pre_filter_graph[1][2]['allowed_instruments'] = ['trumpet', 'trombone']
pre_filter_graph[3][0]['allowed_instruments'] = ['trumpet']

# For filtering by edge value equality
expected_filtered[1][2]['trombone_count'] = 76
expected_filtered[2][3]['trombone_count'] = 76
# For filtering by edge value inclusion
expected_filtered[1][2]['allowed_instruments'] = ['trumpet', 'trombone']


def test_get_edge_filtered_subgraph():
    query_dict = dict(trombone_count=76)
    res = get_edge_filtered_subgraph(pre_filter_graph, query_dict)

    assert is_label_isomorphic(
        res, expected_filtered,
        graph_label_matchers=[
            GraphLabelMatcher(
                match_type='edge', value_type='categorical',
                labels=['descriptor']
            ),
            GraphLabelMatcher(
                match_type='edge', value_type='numerical',
                labels=['trombone_count']
            ),
        ]
    )

    assert not is_label_isomorphic(
        res, pre_filter_graph,
        graph_label_matchers=[
            GraphLabelMatcher(
                match_type='edge', value_type='categorical',
                labels=['descriptor']
            ),
            GraphLabelMatcher(
                match_type='edge', value_type='numerical',
                labels=['trombone_count']
            ),
        ]
    )

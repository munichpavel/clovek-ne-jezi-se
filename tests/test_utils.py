from math import sqrt, pi
from copy import deepcopy

import pytest

import numpy as np

import networkx as nx

from networkx.algorithms import isomorphism as iso

from clovek_ne_jezi_se.utils import (
    make_even_points_on_circle, make_dict_from_lists,
    GraphAnnotationMatcher,
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


# Test GraphAnnotationMatcher
@pytest.mark.parametrize(
    'matcher_args',
    [
        (dict(match_type='duck', value_type='numerical', labels=['a_label'])),
        (dict(match_type='node', value_type='tubular', labels=['a_label'])),
    ]
)
def test_graph_annotation_matcher_errors(matcher_args):
    with pytest.raises(ValueError):
        GraphAnnotationMatcher(**matcher_args)


@pytest.mark.parametrize(
    'matcher,expected_match_function',
    [
        (
            GraphAnnotationMatcher(
                match_type='node', value_type='numerical',
                labels=['a_number']
            ),
            iso.numerical_node_match(['a_number'], [np.nan])
        ),
        (
            GraphAnnotationMatcher(
                match_type='node', value_type='categorical',
                labels=['a_category']
            ),
            iso.categorical_node_match(['a_category'], [None])
        ),
        (
            GraphAnnotationMatcher(
                match_type='edge', value_type='numerical',
                labels=['a_number']
            ),
            iso.numerical_edge_match(['a_number'], [np.nan])
        ),
        (
            GraphAnnotationMatcher(
                match_type='edge', value_type='categorical',
                labels=['a_category']
            ),
            iso.categorical_edge_match(['a_category'], [None])
        ),
    ]
)
def test_graph_annotation_matcher(matcher, expected_match_function):
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
    'graph,other,graph_annotation_matcher,expected',
    [
        (
            two_cycle_digraph, labeled_two_cycle_digraph,
            # dict(categorical_node_labels=['descriptor']),
            GraphAnnotationMatcher(
                match_type='node', value_type='categorical',
                labels=['descriptor']
            ),
            False
        ),
        (
            labeled_two_cycle_digraph, labeled_two_cycle_digraph,
            GraphAnnotationMatcher(
                match_type='node', value_type='categorical',
                labels=['descriptor']
            ),
            True
        ),
        (
            labeled_two_cycle_digraph, other_labeled_two_cycle_digraph,
            GraphAnnotationMatcher(
                match_type='node', value_type='categorical',
                labels=['descriptor']
            ),
            True
        ),
        (
            labeled_two_cycle_digraph, other_labeled_two_cycle_digraph,
            GraphAnnotationMatcher(
                match_type='node', value_type='categorical',
                labels=['descriptor', 'sign']
            ),
            False
        ),
        (
            labeled_two_cycle_digraph, labeled_two_cycle_digraph,
            GraphAnnotationMatcher(
                match_type='node', value_type='numerical',
                labels=['trombone_count']
            ),
            True
        ),
        (
            labeled_two_cycle_digraph, other_labeled_two_cycle_digraph,
            GraphAnnotationMatcher(
                match_type='node', value_type='numerical',
                labels=['trombone_count']
            ),
            False
        ),
        (
            labeled_two_cycle_digraph, labeled_two_cycle_digraph,
            GraphAnnotationMatcher(
                match_type='edge', value_type='categorical',
                labels=['color']
            ),
            True
        ),
        (
            labeled_two_cycle_digraph, other_labeled_two_cycle_digraph,
            GraphAnnotationMatcher(
                match_type='edge', value_type='categorical',
                labels=['color']
            ),
            True
        ),
        (
            labeled_two_cycle_digraph, other_labeled_two_cycle_digraph,
            GraphAnnotationMatcher(
                match_type='edge', value_type='categorical',
                labels=['color', 'mood']
            ),
            False
        ),
        (
            labeled_two_cycle_digraph, labeled_two_cycle_digraph,
            GraphAnnotationMatcher(
                match_type='edge', value_type='numerical',
                labels=['strength']
            ),
            True
        ),
        (
            labeled_two_cycle_digraph, other_labeled_two_cycle_digraph,
            GraphAnnotationMatcher(
                match_type='edge', value_type='numerical',
                labels=['strength']
            ),
            False
        ),

    ]
)
def test_is_labeled_isomorphic(
    graph, other, graph_annotation_matcher, expected
):
    assert is_labeled_isomorphic(graph, other, graph_annotation_matcher) \
        == expected


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

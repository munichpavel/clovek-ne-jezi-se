from math import sqrt, pi
from copy import deepcopy

import pytest

import numpy as np

import networkx as nx

from networkx.algorithms import isomorphism as iso

from clovek_ne_jezi_se.utils import (
    make_even_points_on_circle, make_dict_from_lists,
    GraphQueryParams,
    is_label_isomorphic,
    get_filtered_subgraph_view,
    get_filtered_node_names
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


# Tests of graph utility functions

# Tests for graph filtering
@pytest.mark.parametrize(
    'args,expected',
    [
        (
            dict(graph_component='node', query_type='equality',
                 label='descriptor', value='yutz'),
            'categorical'
        ),
        (
            dict(graph_component='node', query_type='equality',
                 label='trombone_count', value=76),
            'numerical'
        )
    ]
)
def test_graph_query_params_value_type(args, expected):
    query_params = GraphQueryParams(**args)
    query_params.set_value_type()

    assert query_params.value_type == expected


@pytest.mark.parametrize(
    'args,Error',
    [
        (
            dict(graph_component='node', query_type='equality',
                 label='descriptor'),
            TypeError
        ),
        (
            dict(graph_component='node', query_type='equality',
                 value='yutz'),
            TypeError
        ),
        (
            dict(label='descriptor', query_type='equality', value='yutz'),
            TypeError
        ),
        (
            dict(graph_component='node', query_type='equality',
                 label='descriptor', value=None),
            TypeError
        ),
        (
            dict(graph_component='bupkis', query_type='equality',
                 label='descriptor', value='yutz'),
            ValueError
        ),
        (
            dict(graph_component='edge', query_type='goyish',
                 label='descriptor', value='yutz'),
            ValueError
        )
    ]
)
def test_graph_query_params_errors(args, Error):
    with pytest.raises(Error):
        query_params = GraphQueryParams(**args)
        query_params.set_value_type()


@pytest.mark.parametrize(
    'query_param_args,expected_match_function',
    [
        (
            dict(graph_component='node', label='a_number',
                 value_type='numerical'),
            iso.numerical_node_match('a_number', np.nan)
        ),
        (
            dict(graph_component='node', label='a_category',
                 value_type='categorical'),
            iso.categorical_node_match('a_category', None)
        ),
        (
            dict(graph_component='edge', value_type='numerical',
                 label='a_number'),
            iso.numerical_edge_match('a_number', np.nan)
        ),
        (
            dict(graph_component='edge', value_type='categorical',
                 label='a_category'),
            iso.categorical_edge_match('a_category', None)
        ),
    ]
)
def test_graph_query_params_match_fn(
    query_param_args, expected_match_function
):
    # Comparing byte code idea from
    # https://stackoverflow.com/questions/20059011/check-if-two-python-functions-are-equal
    query_params = GraphQueryParams(**query_param_args)
    if query_params.value is not None:
        query_params.set_value_type()
    assert query_params.get_match_function().__code__.co_code == \
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
    #'graph,other,graph_label_matcher,expected',
    'graph,other,query_param_argses,expected',
    [
        (
            two_cycle_digraph, labeled_two_cycle_digraph,
            [dict(graph_component='node',
                  label='descriptor', value_type='categorical')],
            False
        ),
        (
            labeled_two_cycle_digraph, deepcopy(labeled_two_cycle_digraph),
            [dict(graph_component='node',
                  label='descriptor', value_type='categorical')],
            True
        ),
        (
            labeled_two_cycle_digraph, other_labeled_two_cycle_digraph,
            [dict(graph_component='node',
                  label='descriptor', value_type='categorical')],
            True
        ),
        (
            labeled_two_cycle_digraph, labeled_two_cycle_digraph,
            [dict(graph_component='node',
                  label='trombone_count', value_type='numerical')],
            True
        ),
        (
            labeled_two_cycle_digraph, other_labeled_two_cycle_digraph,
            [dict(graph_component='node',
                  label='trombone_count', value_type='numerical')],
            False
        ),
        (
            labeled_two_cycle_digraph, labeled_two_cycle_digraph,
            [dict(graph_component='edge',
                  label='color', value_type='categorical')],
            True
        ),
        (
            labeled_two_cycle_digraph, other_labeled_two_cycle_digraph,
            [dict(graph_component='edge',
                  label='color', value_type='categorical')],
            True
        ),
        (
            labeled_two_cycle_digraph, deepcopy(labeled_two_cycle_digraph),
            [dict(graph_component='edge', label='strength',
                  value_type='numerical')],
            True
        ),
        (
            labeled_two_cycle_digraph, other_labeled_two_cycle_digraph,
            [dict(graph_component='edge', label='strength',
                  value_type='numerical')],
            False
        ),

    ]
)
def test_is_label_isomorphic(
    graph, other, query_param_argses, expected
):
    query_paramses = []
    for args in query_param_argses:
        query_params = GraphQueryParams(**args)
        query_paramses.append(query_params)

    assert is_label_isomorphic(graph, other, query_paramses) \
        == expected


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

# For filtering by edge value equality
pre_filter_graph[0][1]['trombone_count'] = 0
pre_filter_graph[1][2]['trombone_count'] = 76
pre_filter_graph[2][3]['trombone_count'] = 76

# For filtering by edge value inclusion, note that not all edges are labeled
pre_filter_graph[0][1]['allowed_instruments'] = ['trumpet']
pre_filter_graph[1][2]['allowed_instruments'] = ['trumpet', 'trombone']
pre_filter_graph[2][3]['allowed_instruments'] = ['trombone']

# For filtering by edge value equality
expected_filtered[1][2]['trombone_count'] = 76
expected_filtered[2][3]['trombone_count'] = 76
# For filtering by edge value inclusion
expected_filtered[1][2]['allowed_instruments'] = ['trumpet', 'trombone']
expected_filtered[2][3]['allowed_instruments'] = ['trombone']


@pytest.mark.parametrize(
    'graph,query_param_argses,match_candidate,expected',
    [
        (
            pre_filter_graph,
            [dict(graph_component='node', query_type='equality',
                  label='descriptor', value='schlemiel')],
            nx.DiGraph(), True
        ),
        (
            pre_filter_graph,
            [dict(graph_component='node', query_type='equality',
                  label='descriptor', value='yutz')],
            expected_filtered, True
        ),
        (
            pre_filter_graph,
            [
                dict(graph_component='node', query_type='equality',
                     label='descriptor', value='yutz'),
            ],
            expected_filtered, True
        ),
        (
            pre_filter_graph,
            [dict(graph_component='node', query_type='equality',
                  label='descriptor', value='yutz')],
            pre_filter_graph, False  # as pre and post filter graphs are same
        ),
        (
            pre_filter_graph,
            [dict(graph_component='edge', query_type='equality',
                  label='trombone_count', value=76)],
            expected_filtered, True
        ),
        (
            pre_filter_graph,
            [dict(graph_component='edge', query_type='equality',
                  label='trombone_count', value=76)],
            pre_filter_graph, False  # as pre and post filter graphs are same
        ),
        (
            pre_filter_graph,
            [dict(graph_component='edge', query_type='inclusion',
                  label='allowed_instruments', value='trombone')],
            expected_filtered, True
        ),
        (
            pre_filter_graph,
            [dict(graph_component='edge', query_type='inclusion',
                  label='allowed_instruments', value='trumpet')],
            expected_filtered, False  # as query is for trumpets
        ),
    ]
)
def test_get_filtered_subgraph_view(
    graph, query_param_argses, match_candidate, expected
):
    query_paramses = []
    for args in query_param_argses:
        query_params = GraphQueryParams(**args)
        if query_params.value_type is None:
            query_params.set_value_type()
        query_paramses.append(query_params)

    res = get_filtered_subgraph_view(graph, query_paramses)

    assert is_label_isomorphic(res, match_candidate, query_paramses) \
        == expected


@pytest.mark.parametrize(
    'graph,query_param_argses,expected',
    [
        (
            pre_filter_graph,
            [
                dict(graph_component='node', query_type='equality',
                     label='descriptor', value='schlamazel')
            ],
            [0]
        ),
        (
            expected_filtered,
            [
                dict(graph_component='node', query_type='equality',
                     label='descriptor', value='schlamazel')
            ],
            []
        ),
    ]
)
def test_get_filtered_node_names(graph, query_param_argses, expected):
    query_paramses = []
    for args in query_param_argses:
        query_params = GraphQueryParams(**args)
        query_params.set_value_type()
        query_paramses.append(query_params)
    assert get_filtered_node_names(graph, query_paramses) == expected

from math import sqrt, pi

import pytest

import numpy as np

from clovek_ne_jezi_se.utils import (
    make_even_points_on_circle, make_dict_from_lists,
    get_node_filtered_subgraph
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

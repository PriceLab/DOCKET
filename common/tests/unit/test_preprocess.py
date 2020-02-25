"""
This file contains unit tests for functions defined in common/preprocess.py
"""

import pytest
import common.preprocess as preprocess

# Input for pad_tabular and tabular2json tests
data = [['A'], ['B', 'C'], ['D', 'E', 'F']]
rlabels = ['R0', 'R1', 'R2']
clabels = ['C0', 'C1', 'C2']


@pytest.mark.parametrize(
    "input_data, size, value, expected_result",
    [
        (data, None, None, [['A', 0., 0.], ['B', 'C', 0.], ['D', 'E', 'F']]),
        (data, 4, None, [['A', 0., 0., 0.], ['B', 'C', 0., 0.], ['D', 'E', 'F', 0.]]),
        (data, None, 1., [['A', 1., 1.], ['B', 'C', 1.], ['D', 'E', 'F']]),
        (data, 4, 1., [['A', 1., 1., 1.], ['B', 'C', 1., 1.], ['D', 'E', 'F', 1.]]),
        (data, 2, "NA", [['A', "NA"], ['B', 'C'], ['D', 'E']]),
        (data, 3, "NA", [['A', "NA", "NA"], ['B', 'C', "NA"], ['D', 'E', 'F']]),
        (data, 4, "NA", [['A', "NA", "NA", "NA"], ['B', 'C', "NA", "NA"], ['D', 'E', 'F', "NA"]])
    ]
)
def test_pad_tabular(input_data, size, value, expected_result):
    # Convenience function for checking correct results
    def equal(actual, expected):
        return all([all([v1 == v2 for v1, v2 in zip(list1, list2)]) for list1, list2 in zip(actual, expected)])

    actual_result = preprocess.pad_tabular_data(input_data, size, value)
    assert equal(actual_result, expected_result)


@pytest.mark.parametrize(
    "input_data, row_labels, col_labels, by_col, pad_rows, expected_result",
    [
        (data, rlabels, clabels, False, False,
            {'R0': {'C0': 'A'},
             'R1': {'C0': 'B', 'C1': 'C'},
             'R2': {'C0': 'D', 'C1': 'E', 'C2': 'F'}}),
        (data, rlabels, clabels, False, True,
            {'R0': {'C0': 'A', 'C1': '', 'C2': ''},
             'R1': {'C0': 'B', 'C1': 'C', 'C2': ''},
             'R2': {'C0': 'D', 'C1': 'E', 'C2': 'F'}}),
        (data, rlabels, clabels, True, False, {}),
        (data, rlabels, clabels, True, True,
            {'C0': {'R0': 'A', 'R1': 'B', 'R2': 'D'},
             'C1': {'R0': '', 'R1': 'C', 'R2': 'E'},
             'C2': {'R0': '', 'R1': '', 'R2': 'F'}}),
        (data, rlabels[:2], clabels[:2], False, True,
            {'R0': {'C0': 'A', 'C1': ''},
             'R1': {'C0': 'B', 'C1': 'C'}}),
        (data, rlabels[:1], clabels[:1], False, True,
            {'R0': {'C0': 'A'}})
    ]
)
def test_tabular2json(input_data, row_labels, col_labels, by_col, pad_rows, expected_result):
    # Convenience function for checking correct results
    def equal(actual, expected):
        inputs_equal = (set(actual.keys()) == set(expected.keys()))
        inputs_equal = inputs_equal and \
            all([set(v1.keys()) == set(v2.keys()) for v1, v2 in zip(actual.values(), expected.values())])
        inputs_equal = inputs_equal and \
            all([set(v1.values()) == set(v2.values()) for v1, v2 in zip(actual.values(), expected.values())])
        return inputs_equal

    actual_result = preprocess.tabular2json(input_data, row_labels, col_labels, by_col, pad_rows)
    assert equal(actual_result, expected_result)

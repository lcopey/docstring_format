"""Custom function in the parser"""
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    import pandas as pd


def identity(x):
    """Convenience function returning the input value"""
    return x


def _get_ref_values(values: "Union[pd.DataFrame, pd.Series]", ref_id):
    """Get reference from values either as scalar or as numpy array"""
    ref_values = values.loc[ref_id]
    if isinstance(ref_id, list):
        ref_values = ref_values.values
    return ref_values


def relative_percentage(
    values: "Union[pd.DataFrame, pd.Series]", ref_id
) -> "Union[pd.DataFrame, pd.Series]":
    """Compute the percentage of varation of values relative to the value in ref_id"""
    ref_values = _get_ref_values(values, ref_id)
    return (values - ref_values) / ref_values


def delta(
    values: "Union[pd.DataFrame, pd.Series]", ref_id
) -> "Union[pd.DataFrame, pd.Series]":
    """Compute the difference of values with respect to ref_id.

    Parameters
    ----------
    values: values to compute from
    ref_id: delta values are computed with respect to that reference. It should be valid index or a list of valid
     index from values.
    -------

    """
    ref_values = _get_ref_values(values, ref_id)
    return values - ref_values

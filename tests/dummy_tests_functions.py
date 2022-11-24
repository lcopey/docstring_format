from typing import Iterable, Optional, Union
import pandas as pd


def function1(arg1: str):
    """
    AZrojrltndflg lejkkjntgdf

    Parameters
    ----------
    arg1: test

    Returns
    -------

    """
    pass


def function2(arg1: list, ) -> str:
    """A function doing something


    Second paragraph.
    
    Third paragraph
    Parameters
    ----------
    arg1 (list): This does something

    """
    pass


def function3(arg1: Optional[Iterable] = None) -> dict:
    """

    Parameters
    ----------
    arg1

    Returns
    -------

    """
    pass


def function4(arg1: Optional[Iterable] = None, arg2: Optional[tuple] = None) -> dict:
    """

    Parameters
    ----------
    arg1: this does that

    Returns
    -------

    """
    pass


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
    # ref_values = _get_ref_values(values, ref_id)
    # return values - ref_values
    pass


def delta_w_returns(
        values: Union[pd.DataFrame, pd.Series], ref_id
) -> Union[pd.DataFrame, pd.Series]:
    """Compute the difference of values with respect to ref_id.

    Parameters
    ----------
    values: values to compute from
    ref_id: delta values are computed with respect to that reference. It should be valid index or a list of valid
     index from values.

    Returns
    -------

    """
    # ref_values = _get_ref_values(values, ref_id)
    # return values - ref_values
    pass

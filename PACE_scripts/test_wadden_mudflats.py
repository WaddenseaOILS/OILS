"""
tests for wadden_mudflat code
"""

import pytest


from datetime import datetime
import numpy as np

from wadden_mudflats import Delft3D_Mudflats

import gridded

infile = "./PACE_GNOME_01V2.nc"


@pytest.fixture
def dataset():
    ds = gridded.Dataset(infile)

    return ds


def test_init(dataset):

    tf = Delft3D_Mudflats(dataset)

    assert True


def test_no_depth():
    ds = gridded.Dataset()
    ds.variables = {}  # just so there is something
    with pytest.raises(ValueError):
        tf = Delft3D_Mudflats(ds)


def test_contents(dataset):
    """
    checking that the dataset loaded correctly

    not really a job for these tests, but ...
    """
    print dataset.info

    depth = dataset.variables['depth']

    print depth.time.info


def test_is_dry(dataset):

    # depth and time where tehre is some dry
    tf = Delft3D_Mudflats(dataset, dry_depth=0.0)

    points = ((5.2, 53.3),
              (5.3, 53.3),
              (5.2, 53.25),
              (5.424411, 53.218140),
              )

    time = datetime(2009, 1, 15, 6)

    result = tf.is_dry(points, time)

    print result

    assert np.alltrue(result == [False, True, True, False])


def test_outside_grid(dataset):
    """
    what happens is the elements are outside the grid??

    should always be True

    """

    tf = Delft3D_Mudflats(dataset, dry_depth=-10000)  # make sure nothing is dry

    points = ((3.5, 54.0),  # off
              (7.5, 53.4),  # off
              (6.0, 52.0),  # off
              (5.3, 53.3),  # on
              (5.2, 53.25),  # on
              )

    time = datetime(2009, 1, 15, 0)

    result = tf.is_dry(points, time)

    print "results", result

    assert list(result) == [True, True, True, False, False]



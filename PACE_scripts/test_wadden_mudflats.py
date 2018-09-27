"""
tests for wadden_mudflat code
"""

from datetime import datetime

import pytest
from wadden_mudflats import Delft3D_Mudflats

import gridded


infile = "../PACE_GNOME_01V2.nc"


@pytest.fixture
def dataset():
    grid_topology = {"node_lat": "latc",
                     "node_lon": "lonc",
                     "center_lon": "lon",
                     "center_lat": "lat",
                     }

    ds = gridded.Dataset(infile, grid_topology=grid_topology)

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

    tf = Delft3D_Mudflats(dataset)

    points = ((53.3, 5.2),
              (53.3, 5.3),
              (53.25, 5.2)
              )

    time = datetime(2009, 1, 15, 0)

    result = tf.is_dry(points, time)

    print result

    assert False



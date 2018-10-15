#!/usr/bin/env python

"""
wadden_mudflats.py

implementation of a py_gnome Tideflats object that works with the Matroos RWS model results.
"""

import gridded
import numpy as np
from gnome.maps.tideflat_map import TideflatBase


class Matroos_Mudflats(TideflatBase):
    def __init__(self, dataset, dry_vel_u=-9999.0, grid_topology=None):
        """
        initilize a Mudflats object for Matroos Files

        :param dataset: a dataset with a VELU Variable
        :type dataset: gridded.Dataset

        :param dry_vel_u=-9999.0: vel_u == -9999.0 which is masked/undefined meaning a tidal flat is considered dry
        :type dry_vel_u: float
        """
        # check if given dataset is instance of gridded.Dataset
        if isinstance(dataset, gridded.Dataset):
            self.dataset = dataset
        # add grid_topology for rgrid
        else:
            self.dataset = gridded.Dataset(dataset, grid_topology=grid_topology)

        self.dry_vel_u = dry_vel_u

        try:
            self.vel_u = self.dataset.variables['VELU']
        except KeyError:
            raise ValueError('Dataset must have a "VELU" variable')

    def is_dry(self, points, model_time):
        """
        overriding of is_dry -- returns True for elements that are
        located where the vel_u is equal to the sepecified dry_vel_u

        Note: that elements off the grid will get True -- as though
              they are on a mudflat -- this means that elements in
              between the grid and the shoreline will always be on
              a mudflat

              maybe there is a better way to handle this?
        """
        vel_u = self.vel_u
        # extract the current timeslice
        # FIXME: can this be done all at once with a netcdf variable?
        t_ind = vel_u.time.index_of(model_time)

        vel_u_at_t = vel_u.data[t_ind]

        # find the cells the elements are in:
        # add 1 for padding
        cell_ind = vel_u.grid.locate_faces(points[:, :2]) + 1
        # print np.ma.masked_array(d_at_t).filled()
        if isinstance(cell_ind, np.ma.masked_array):
            cell_ind = cell_ind.data

        off_grid = (cell_ind[:, 0] == -1) & (cell_ind[:, 0] == -1)

        velocity_u = vel_u_at_t[cell_ind[:, 0], cell_ind[:, 1]]
        velocity_u = np.ma.masked_array(velocity_u).filled()
        dry = velocity_u == -9999.0

        # elements off grid will get -1 -- so valid, but incorrect
        # so reset here.
        # must be False, as otherwise they would never move again.
        # though if there is a gap between the grid and the shoreline,
        # this won't be technically right, but should be reasonable
        dry[off_grid] = False

        return dry

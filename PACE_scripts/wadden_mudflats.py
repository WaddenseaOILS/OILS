#!/usr/bin/env python

"""
wadden_mudflats.py

implementation of a py_gnome Tideflats object that works with the

Delft3d PACE model results.
"""

import numpy as np

import gridded

from gnome.maps.tideflat_map import TideflatBase


class Delft3D_Mudflats(TideflatBase):
    def __init__(self, dataset, dry_depth=0.0):
        """
        initilize a Mudflats object

        :param dataset: a dataset with a depth Variable
        :type dataset: gridded.Dataset

        :param dry_depth=0.0: depth below which a tidal flat is considered dry
        :type dry_depth: float
        """

        if isinstance(dataset, gridded.Dataset):
            self.dataset = dataset
        else:
            self.dataset = gridded.Dataset(dataset)

        self.dry_depth = dry_depth

        try:
            self.depth = self.dataset.variables['depth']
        except KeyError:
            raise ValueError('Dataset must have a "depth" variable')

    def is_dry(self, points, model_time):
        """
        overriding of is_dry -- returns True for elements that are
        located where the depth is less than the specified dry_depth

        Note: that elements off the grid will get True -- as though
              they are on a mudflat -- this means that elements in
              between the grid and the shoreline will always be on
              a mudflat

              maybe there is a better way to handle this?
        """
        depth = self.depth
        # extract the current timeslice
        # FIXME: can this be done all at once with a netcdf variable?
        t_ind = depth.time.index_of(model_time)

        d_at_t = depth.data[t_ind]

        # find the cells the elements are in:
        # add 1 for padding

        cell_ind = depth.grid.locate_faces(points[:,:2], 'node') + 1

        if isinstance(cell_ind, np.ma.masked_array):
            cell_ind = cell_ind.data

        off_grid = (cell_ind[:, 0] == -1) & (cell_ind[:, 0] == -1)

        depths = d_at_t[cell_ind[:, 0], cell_ind[:, 1]]
        dry = depths < self.dry_depth

        # elements off grid will get -1 -- so valid, but incorrect
        # so reset here.
        dry[off_grid] = True

        return dry

#!/usr/bin/env python

"""
wadden_mudflats.py

implementation of a py_gnome Tideflats object that works with the

Delft3d PACE model results.
"""

from gnome.maps.tideflat_map import TideflatBase


class Delft3D_Mudflats(TideflatBase):
    def __init__(self, dataset):
        """
        initilize a Mudflats object

        :param dataset: a dataset with a depth Variable
        :type dataset: gridded.Dataset
        """

        self.dataset = dataset

        try:
            self.depth = dataset.variables['depth']
        except KeyError:
            raise ValueError('Dataset must have a "depth" variable')

        print "depth is:", self.depth.info

    def is_dry(self, points, model_time):

        depths = self.depth.at(points, model_time)

        print "depths, ", depths






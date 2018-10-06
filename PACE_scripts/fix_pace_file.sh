#!/bin/bash

# **NOTE:** this actually breaks the file
#           it turns out that the face dimensions are
#            supposed to be bigger than the node dimensions.
# I'm still confused :-(

# shell script that uses NCO to "fix" the data file

# rename the variables

ncrename -v lonc,node_lon \
         -v latc,node_lat \
         -v lat,center_lat \
         -v lon,center_lon \
         PACE_GNOME_01V2.nc PACE_GNOME_01V2_fixed.nc

# grid:face_dimensions = "x: xc (padding: both) y: yc (padding: both)" ;
# rename the attributes of the grid variable
ncatted -a node_coordinates,grid,m,c,'node_lon node_lat' \
        -a node_dimensions,grid,m,c,'x y' \
        -a face_coordinates,grid,m,c,'center_lon center_lat' \
        -a face_dimensions,grid,m,c,'x: xc (padding: both) y: yc (padding: both)' \
        -a long_name,node_lon,m,c,'Y-coordinate of grid points' \
        -a long_name,node_lat,m,c,'X-coordinate of grid points' \
        -a long_name,center_lon,m,c,'Y-coordinate of cell centres' \
        -a long_name,center_lat,m,c,'X-coordinate of cell centres' \
        -a node_dimension,grid,d,, \
        -a units,grid,d,, \
        PACE_GNOME_01V2_fixed.nc



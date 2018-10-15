#!/usr/bin/env python2

import os

# This brings in the common names needed to run py_gnome
# for the "usual" cases.
import gnome.scripting as gs
from gnome.environment import TimeseriesData
from gnome.maps.tideflat_map import TideflatMap
# still need these, 'cause we're doing something special here.
from gnome.movers import PyCurrentMover
from gnome.utilities.time_utils import asdatetime

from wadden_mudflats_matroos import Matroos_Mudflats

data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))

# Simulation outputs:
# use this place to script the folder based on test number or something
# it will be a relative path to this script
out_dir = 'mudflat_matroos_test_real'

# Model parameters:
start_time = "2018-10-11 05:00"  # time 00:00 if you don't specify
model_duration = gs.hours(24)

dT_OUT = gs.minutes(30)

currentfile = 'MatroosRect.nc'

# constant wind (in both time and space)
Wind = {"speed": 10, "direction": 270, "units": "m/s"}

SpillPosition = (5.122382, 53.327899, 0) # tussen VL en TX
# SpillPosition = (5.210218, 53.231510, 0)  # route Harlingen Terschelling
# SpillPosition = (4.834194, 52.936454, 0)

# Model Parameters:
base_dir = os.path.dirname(__file__)
newpath = os.path.join(base_dir, out_dir)

if not os.path.exists(newpath):
    os.makedirs(newpath)

print 'init model'
model = gs.Model(start_time=start_time,
                 duration=model_duration,
                 time_step=gs.minutes(1)
                 )

print 'Loading current'
topology = {'grid_type': 'rgrid', 'node_lon': 'x', 'node_lat': 'y'}
current = gs.GridCurrent.from_netCDF(os.path.join(data_dir, currentfile), grid_topology=topology)
angle = TimeseriesData.constant(name='angle', data=17.0, units='degrees')

current.angle = angle
current_mover = PyCurrentMover(current=current)

print 'Adding  map'

tideflat = Matroos_Mudflats(os.path.join(data_dir, currentfile), grid_topology=topology)

mapfile = 'Waddensea_ijsselmeer_6.bna'
land_map = gs.MapFromBNA(mapfile)

model.map = TideflatMap(land_map, tideflat)

print 'Adding current'
model.movers += current_mover

print 'Adding RandomMover'
model.movers += gs.RandomMover(diffusion_coeff=50000)

print 'adding a wind mover:'

model.movers += gs.constant_wind_mover(**Wind)

print 'adding spill'
spill = gs.surface_point_line_spill(num_elements=100,
                                    start_position=SpillPosition,
                                    end_position=(SpillPosition[0],
                                                  SpillPosition[1]-0.1,
                                                  0),
                                    release_time=asdatetime(start_time),
                                    amount=5000,
                                    units='kg',
                                    name='My spill')
model.spills += spill

model.outputters += gs.NetCDFOutput(os.path.join(out_dir, 'test_output.nc'),
                                    which_data='most',
                                    output_timestep=dT_OUT)

renderer = gs.Renderer(output_timestep=dT_OUT,
                       map_filename=mapfile,
                       output_dir=out_dir,
                       formats=['gif'],  # ['gif', 'png']
                       image_size=(1280, 1024),
                       viewport=((4.5, 53.0),
                                 (5.5, 53.5))
                       )
model.outputters += renderer

gs.set_verbose()  # get some more info as the model runs

print "Doing a full run:"
model.full_run()

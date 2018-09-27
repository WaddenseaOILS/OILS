"""checking a not-properly compliant dataset"""


from datetime import datetime
import gridded

filename = "../PACE_GNOME_01V2.nc"
# filename = "../PACE_GNOME_01V2_fixed.nc"

# grid_topology = {"node_lat": "latc",
#                  "node_lon": "lonc",
#                  "center_lon": "lon",
#                  "center_lat": "lat",
#                  }

ds = gridded.Dataset("../PACE_GNOME_01V2.nc",
                     # grid_topology=grid_topology
                     )


print ds

depth = ds.variables['depth']

print depth
print depth.grid

# see if we can interpolate

points = ((5.2, 53.3),
          (5.3, 53.3),
          (5.2, 53.25)
          )


# should be middle of the timespan in the file
time = datetime(2009, 1, 15)

print "finding values at location and time:"
print depth.at(points, time)

grid = ds.grid

print "locating the faces on node"
print grid.locate_faces(points, 'node')

# why does this fail??
print "locating the faces on center"
print grid.locate_faces(points, 'center')






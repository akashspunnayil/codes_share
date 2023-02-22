import abfile.abfile as abf # works for python3
from netCDF4 import Dataset
#import abfile as abf # works for python2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from netCDF4 import Dataset
# import glob
from matplotlib import rc, rcParams
import cartopy.crs as ccrs
import cartopy.feature as cfeature


def India_Map():
    fig = plt.figure(figsize=[20,10])
    #proj=ccrs.SouthPolarStereo(central_longitude=78.0)
    proj=ccrs.Stereographic(central_latitude=0.0,central_longitude=80.0)
    ax = plt.axes(projection=proj)
    #ax.set_extent([-179,179, -90, 40],ccrs.PlateCarree())
    ax.set_extent([30, 110, -60, 40]) #],ccrs.PlateCarree())
    #ax.coastlines(resolution='50m', color='gray')
    #ax.add_feature(cfeature.LAND)
    #ax.gridlines(draw_labels=True, dms=False, x_inline=False, y_inline=False) #dms=False for native grid
    return fig,ax,proj

topo_file1='depth_INDa0.12_01.a'

grdname = 'regional.grid.a'
grdfile = abf.ABFileGrid(grdname,"r")
plon=grdfile.read_field("plon")
plat=grdfile.read_field("plat")
idm,jdm =plon.shape
tf=abf.AFile(jdm,idm,topo_file1,"r")
topo1=tf.read_record(0)
tf.close()


ncfile='section001.nc';
fh =  Dataset(ncfile, mode='r')
lon = fh.variables['lon'][:]
lat = fh.variables['lat'][:]

df = pd.read_csv('section001.dat', sep="\s+", skiprows=1, names=['A','B','C','D','E','F','G','H'])
#df

fig,ax,proj=India_Map()
plt.contourf(plon, plat, topo1,0,transform=ccrs.PlateCarree())
#plt.scatter(df['A'], df['B'], s=5, color='red') # FOR NATIVE GRID
plt.scatter(df['C'], df['D'], s=5, color='red', transform=ccrs.PlateCarree()) # FOR REGULAR GRID


#fig = plt.figure(figsize=[8,12])
#plt.contourf(topo1)
#plt.scatter(lon, lat)
#plt.scatter(df['A'], df['B'], s=5, color='red') # FOR NATIVE GRID

#plt.text(-0.1, 0.55, 'latitude', va='bottom', ha='center',
#        rotation='vertical', rotation_mode='anchor', fontsize=14)
#plt.text(0.5, -0.08, 'longitude', va='bottom', ha='center',
#        rotation='horizontal', rotation_mode='anchor', fontsize=14)

coastline_50m = cfeature.NaturalEarthFeature('physical', 'coastline', '110m', edgecolor='grey', facecolor='w')
                        #facecolor=cfeature.COLORS['land'])
ax.add_feature(coastline_50m)

plt.savefig('section_location_test.png',bbox_inches='tight')#,dpi=90)


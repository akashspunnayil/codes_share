import abfile.abfile as abf # works for python3
#import abfile as abf # works for python2
import numpy as np
import matplotlib.pyplot as plt
# from netCDF4 import Dataset
# import glob
from matplotlib import rc, rcParams

import cartopy.crs as ccrs
import cartopy.feature as cfeature



def India_Map():
    fig = plt.figure(figsize=[20,10])
    #proj=ccrs.SouthPolarStereo(central_longitude=78.0) # worked but turned-off for STEREOGRAPHIC PROJECTION
    proj=ccrs.Stereographic(central_latitude=10.0,central_longitude=80.0)
    #ax = plt.axes(projection=ccrs.SouthPolarStereo(central_longitude=90.0)) 
    #rotated_crs = ccrs.RotatedPole(pole_longitude=120.0, pole_latitude=90.0)
    ax = plt.axes(projection=proj)
    #ax.set_extent([-45, 120, -75, 30],ccrs.PlateCarree()) 
    ax.set_extent([41,100, -70, 25])#,ccrs.PlateCarree())  # bottom, right, left, top (x0, x1, y0, y1)
    ax.coastlines(resolution='50m', color='gray')
    ax.add_feature(cfeature.LAND)
    #ax.add_feature(cfeature.COASTLINE,scale='high')
    coastline_50m = cfeature.NaturalEarthFeature('physical', 'coastline', '110m',
                        edgecolor='grey', facecolor='w') 
                        #facecolor=cfeature.COLORS['land'])
    ax.add_feature(coastline_50m)
    ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
    ax.set_xlabel('Longitude [deg]', fontsize = 14)
    ax.set_ylabel('Latitude [deg]', fontsize = 14)
    #cbar.set_label('Model resolution (km)', rotation=270)
    
    #return(fig,ax)
    return fig,ax,proj

#pathgrd = '/media/akashs/FA22E72622E6E69B/DATA1_disk/1_NANSEN/2_MODELLING/HYCOM_ECOSMO/compare_relax_forcing/topo/'
pathgrd = '/cluster/work/users/akash2021/INDa0.12/expt_01.2/data/avearchm_ab2nc_2000_2020_new_run/planktons_secprod/'
grdname = pathgrd + 'regional.grid.a'
grdfile = abf.ABFileGrid(grdname,"r")
plon=grdfile.read_field('plon')
plat=grdfile.read_field('plat')
scpx=grdfile.read_field('scpx')
scpy=grdfile.read_field('scpy')
reso = (scpy +scpx)/2000 # (average grid size in km) #*thick[j,i]
idm,jdm=plon.shape
# grdfile.close()


fig,ax,proj=India_Map()
pxy = proj.transform_points(ccrs.PlateCarree(),plon,plat);px=pxy[:,:,0];py=pxy[:,:,1];
#pxy = proj.transform_points(ccrs.Stereographic(),plon,plat);px=pxy[:,:,0];py=pxy[:,:,1];
#ax.add_feature(coastline_50m)
plt.pcolormesh(px,py,reso);cbar=plt.colorbar(shrink=0.8)
cbar.set_label('Model resolution (km)', rotation=270, fontsize=14, labelpad=20)
#plt.set_xlabel('Longitude [deg]', fontsize = 14)
#plt.set_ylabel('Latitude [deg]', fontsize = 14)
#plt.text(200,50,'Model resolution (km)',color='k',fontsize=10)
ax.text(-0.1, 0.55, 'latitude', va='bottom', ha='center',
        rotation='vertical', rotation_mode='anchor',
        transform=ax.transAxes, fontsize=14)
ax.text(0.5, -0.08, 'longitude', va='bottom', ha='center',
        rotation='horizontal', rotation_mode='anchor',
        transform=ax.transAxes, fontsize=14)


#ax=India_Map()
#ax[1].contourf(plon,plat,np.log(reso),50,transform=ccrs.PlateCarree()) # SouthPolarStereo())  #vmin=0,vmax=0.0000005
#ax[1].coastlines()
#ax[1].gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
#plt.contourf(reso);plt.colorbar()
plt.savefig('resolution_plot_TRY_annette.png',bbox_inches='tight',dpi=90)


# #----------------------------
# # Welcome to CPHL PSAL TEMP data reader
# #---------------------------- 
########
#     This file contains all the functions used to process data
########

import pandas as pd
import numpy as np
#----------------------------
# for plotting
#----------------------------
#import cartopy.crs as ccrs
#from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import matplotlib.pyplot as plt
import matplotlib.dates  as mdates
from matplotlib.patches import Polygon
from matplotlib.dates import DateFormatter
import datetime as dt
from datetime import datetime
import scipy

#----------------------------
# for converting time
#  ref: https://forum.marine.copernicus.eu/discussion/274/how-to-convert-netcdf-time-to-python-datetime-resolved/p1
#----------------------------
import cftime

#----------------------------
# for nc file I/O
#----------------------------
import netCDF4 as nc
import gzip
import os
import shutil
import tempfile

import seawater as sw
from seawater.library import T90conv


def open_netcdf(fname):
#----------------------------
# Open netcdf file
#----------------------------
    if fname.endswith(".gz"):
        gzfile = gzip.open(fname, 'rb')
        tmp = tempfile.NamedTemporaryFile(delete=False)
        shutil.copyfileobj(gzfile,tmp)
        gzfile.close()
        tmp.close()
        ncfile = nc.Dataset(tmp.name,'r')
        os.unlink(tmp.name)
    else:
        ncfile = nc.Dataset(fname,'r')
    return ncfile

    
def read_depth_levels(depth_max):
#----------------------------
# read standard depth levels until depth_max depth
#----------------------------
########
#     In : 
#     depth_max(int): maximal depth to keep for computing interpolation and set maximum depth for the rest of the process
########
    dirin  = '/mnt/data01/submapp/gotm'
    file = 'depth_levels.npy'
    infile=dirin+'/'+file
    gotm_dep=-np.flip(np.load(infile)) # depth [meter]
    index_max = abs(gotm_dep - depth_max).argmin() 
    return gotm_dep[:index_max] ## Only depth_max first meters
    
      
    
def read_cphl_data(cphl_directory,gotm_dep):
#----------------------------
# read chlorophylle data
#----------------------------     
########
#     In : 
#     cphl_directory where CPHL nc files are located,
#     gotm_dep: 1D array of size nb_dep containing reference depth data for interpolation

#     Out: 
#     df_cphl: dataframe with following colomns: Argo, nb_time, nb_dep, Latitude, Longitude, Day, Date, Depth level, CPHL_interpolated)
########
########
#     Global operation:
#     -For each Argo floats:
#     -Read each CPHL / PRES / LATTITUDE / LONGITUDE / TIME variables from de .nc file
#     -Create a 1D mask that will ba applied to 1D variables, and to 2D variables (True or False for the entire column, more details below)
#     -Interpolate cphl data on standard depth levels
#     -Manipulate and duplicate data in order to have a meaningfull Dataframe where number of rows = nb_tim * n_dep
########
    os.chdir(cphl_directory) 
    cwd = os.getcwd()
    dir_list_cphl = os.listdir(cwd)
    dir_list_cphl.sort()
    for index_file,file in enumerate(dir_list_cphl):
        infile=cphl_directory+'/'+file
        if os.path.exists(infile):
            print('Read '+file)
            #-- read Argo data
            ncfile = open_netcdf(infile)
            var_cphl_ma = ncfile.variables['CPHL_ADJUSTED'][:,:] # [mg m-3]
            var_cphl_qc_ma = ncfile.variables['CPHL_ADJUSTED_QC'][:,:]           
            var_dep_ma = ncfile.variables['PRES'][:,:]          # [dbar]
            var_lat_ma = ncfile.variables['LATITUDE'][:]        # [degree north]
            var_lon_ma = ncfile.variables['LONGITUDE'][:]       # [degree east]
            var_day_ma = ncfile.variables['TIME'][:]           # [days since 1950-01-01T00:00:00Z]

            ###### Important step ######
            # For each float, we check the mask for every depth level, if there is only True, return True, if only False, return False, if mixed, return False
            msk_cphl = var_cphl_ma.mask
            msk_var_1D = [all(msk_cphl[i,:]) for i in range(msk_cphl.shape[0])]
                
            var_lon=np.ma.compressed(np.ma.array(var_lon_ma.data, mask= msk_var_1D))
            var_lat=np.ma.compressed(np.ma.array(var_lat_ma.data, mask= msk_var_1D))
            var_day=np.ma.compressed(np.ma.array(var_day_ma.data, mask= msk_var_1D))
            
            msk_var_1D=[not elem for elem in msk_var_1D] ### Need to flip the mask for cphl and dep
            var_cphl = var_cphl_ma[msk_var_1D]
            var_dep = var_dep_ma[msk_var_1D]
        else:
            print('Can not find '+file+', EXIT')
            exit()      
           
        nb_tim = np.shape(var_cphl)[0]
        nb_dep = np.shape(gotm_dep)[0]  

        var_date_df, var_cphl_interp_df = interp_cphl(nb_tim,nb_dep,gotm_dep,var_day,var_dep,var_cphl) ## Compute CPHL interpolation on standard depth level
        
        ## The following lines correpsond to data manipulation to create a meaningfull Dataframe
        ## In the end, all variables must be 1D array of size nb_dep * nb_time
        ## So we duplicate name variable nb_dep*nb_time times 
        ## And we duplicate 1D variables nb_dep times
        file = file[9:16]
        var_name_df = np.array([[file]*nb_dep for x in range(nb_tim)]).flatten()

        var_lon_df, var_lat_df, var_day_df, var_dep_df = np.zeros((nb_tim,nb_dep)), np.zeros((nb_tim,nb_dep)), np.zeros((nb_tim,nb_dep)), np.zeros((nb_tim,nb_dep))

        for j in range(nb_tim):
            var_lon_df[j,:] = var_lon[j]
            var_lat_df[j,:] = var_lat[j]
            var_day_df[j,:] = var_day[j]
            var_dep_df[j,:] = gotm_dep

        var_lon_df = var_lon_df.flatten() 
        var_lat_df = var_lat_df.flatten() 
        var_day_df = var_day_df.flatten()
        var_date_df = var_date_df.flatten() 
        var_dep_df = var_dep_df.flatten()
        
        
        #print(np.shape(var_name_df),np.shape(var_nbtim_df),np.shape(var_lat_df),np.shape(var_day_df),np.shape(var_cphl_interp_df),np.shape(var_nbdep_df),np.shape(var_lon_df),np.shape(var_date_df),np.shape(var_dep_df))
        df_cphl_i = pd.DataFrame({"Argo": var_name_df, "Latitude": var_lat_df, "Longitude": var_lon_df, "Day": var_day_df, "Date": var_date_df, "Depth level": var_dep_df, "CPHL": var_cphl_interp_df})

        ### Outliers detected on 690370 file after 2021-05
        if file == "6903570":
            df_cphl_i = df_cphl_i.drop(df_cphl_i[df_cphl_i.Date > np.datetime64("2021-04")].index)     

        if index_file == 0:
            df_cphl = df_cphl_i
        else:
            df_cphl = pd.concat([df_cphl,df_cphl_i], ignore_index = True)
    
    ### Important step ###
    ## While inspecting profiles, we realise that some pocess have been apply to some profiles like 6903569.nc 
    ## This process consists mainly in setting a threshold on CPHL data a bit under 0.05
    ## As a consequence, we decided to apply the same process to all data, by setting a CPHL theshold at 0.05
    df_cphl.loc[df_cphl["CPHL"] < 0.05, "CPHL"] = 0.05
    
    return df_cphl
    
        
def interp_cphl(nb_tim,nb_dep,gotm_dep,var_day,var_dep,var_cphl):
#----------------------------
# Compute CPHL interpolation on standard depth levels
#----------------------------   
########
#     In :
#     nb_tim(int): number of timestamps for the Argo float
#     nb_dep(int): number of depth levels  
#     gotm_dep: 1D array of size nb_dep containing standard depth levels
#     var_day: 1D array of size nb_tim containing all timestamps in Julian days
#     var_dep: 2D array of size nb_tim * unknownsize containing depth levels where each CPHL was monitored
#     var_cphl: 2D array of size nb_tim * unknownsize containing CPHL data

#     Out: 
#     var_date_df: 1D array of size nb_tim*nb_dep containing all recording dates with datetime format, every column of the array is filed with the same date value
#     var_cphl_interp_df: 1D array of size nb_tim*nb_dep containing all CPHL data
########
    start=dt.datetime(1950,1,1,0,0,0)
    chunks_date=[]
    chunks_interp=[]

    for j in range(nb_tim):
        delta=dt.timedelta(var_day[j])
        offset = delta + start
        date = np.array([offset for j in range(nb_dep)])
        chunks_date.append(date)

        var_cphl_1d=var_cphl[j,:].squeeze()
        var_dep_1d=var_dep[j,:].squeeze()
        var_cphl_1d_interp=np.interp(gotm_dep,var_dep_1d,var_cphl_1d)
        chunks_interp.append(var_cphl_1d_interp)

    var_date_df = np.stack(chunks_date, axis=0)    
    chunks_interp = np.array(chunks_interp,dtype='float')
    chunks_interp[chunks_interp <= 0] = np.nan
    var_cphl_interp=np.vstack(chunks_interp)
    var_cphl_interp_df = var_cphl_interp.flatten()
    
    return var_date_df, var_cphl_interp_df
    
            	

def read_psal_temp_data(psal_temp_directory,gotm_dep):
#----------------------------
# read Salinity and Temperature data, basically same operations as with CPHL data
#----------------------------   
########
#     In : 
#     psal_temp_directory where PSAL/TEMP nc files are located,
#     gotm_dep: 1D array of size nb_dep containing reference depth data for interpolation

#     Out: 
#     df_psal_temp: dataframe with following colomns: Argo, nb_time, nb_dep, Latitude, Longitude, Day, Date, Depth level, PSAL_interpolated, TEMP_interpolated, mldT, mldD)
########

    os.chdir(psal_temp_directory) 
    cwd = os.getcwd()
    dir_list_psal_temp = os.listdir(cwd)
    dir_list_psal_temp.sort()
    
    for index_file,file in enumerate(dir_list_psal_temp):
        infile=psal_temp_directory+'/'+file
        
        if os.path.exists(infile):
            print('Read '+file)
            #-- read Argo data
            ncfile = open_netcdf(infile)
            var_psal_ma = ncfile.variables['PSAL_ADJUSTED'][:,:] # 
            var_temp_ma = ncfile.variables['TEMP_ADJUSTED'][:,:]
            var_dep_ma = ncfile.variables['PRES_ADJUSTED'][:,:]          # [dbar]
            var_lat_ma = ncfile.variables['LATITUDE'][:]        # [degree north]
            var_lon_ma = ncfile.variables['LONGITUDE'][:]       # [degree east]
            var_day_ma = ncfile.variables['JULD'][:]           # [days since 1950-01-01T00:00:00Z]

            ###### Important step ######
            # For each float, we check the mask for every depth level, if there is only True, return True, if only False, return False, if mixed, return False
            msk_psal = var_psal_ma.mask
            msk_var_1D = [all(msk_psal[i,:]) for i in range(msk_psal.shape[0])]

            var_lon=np.ma.compressed(np.ma.array(var_lon_ma.data, mask= msk_var_1D))
            var_lat=np.ma.compressed(np.ma.array(var_lat_ma.data, mask= msk_var_1D))
            var_day=np.ma.compressed(np.ma.array(var_day_ma.data, mask= msk_var_1D))
                        
            msk_var_1D=[not elem for elem in msk_var_1D] ### Need to flip the mask for cphl and dep
            var_psal = var_psal_ma[msk_var_1D]
            var_temp = var_temp_ma[msk_var_1D]
            var_dep = var_dep_ma[msk_var_1D]
            
            var_temp = np.where(var_temp > 70, np.nan, var_temp)  ### Remove outliers that should not be there
            var_psal = np.where(var_psal > 70, np.nan, var_psal)  ### As we take mixed masked columns (True / False), some values could be aberrants
            
        else:
            print('Can not find '+file+', EXIT')
            exit()
        
        nb_tim = np.shape(var_psal)[0]
        nb_dep = np.shape(gotm_dep)[0]  

        var_date_df, var_psal_interp, var_temp_interp = interp_psal_temp(nb_tim,nb_dep,gotm_dep,var_day,var_dep,var_psal,var_temp)

        ## The following lines correpsond to data manipulation to create a meaningfull Dataframe
        ## In the end, all variables must be 1D array of size nb_dep * nb_time in order to fit in the Dataframe
        ## So we duplicate name variable nb_dep*nb_time times 
        ## And we duplicate 1D variables nb_dep times
        file = file[:7]
        var_name_df = np.array([[file]*nb_dep for x in range(nb_tim)]).flatten()

        var_lon_df, var_lat_df, var_day_df, var_dep_df, var_mldD_df, var_mldT_df = np.zeros((nb_tim,nb_dep)), np.zeros((nb_tim,nb_dep)), np.zeros((nb_tim,nb_dep)),  np.zeros((nb_tim,nb_dep)), np.zeros((nb_tim,nb_dep)), np.zeros((nb_tim,nb_dep))

        for j in range(nb_tim):
            var_lon_df[j,:] = var_lon[j]
            var_lat_df[j,:] = var_lat[j]
            var_day_df[j,:] = var_day[j]
            var_dep_df[j,:] = gotm_dep

        var_mldT, var_mldD = get_mld(var_psal_interp, var_temp_interp, var_dep_df) ### Compute mixed layer depth thanks to psal and temp data

        for j in range(nb_tim):
            var_mldT_df[j,:] = var_mldT[j]
            var_mldD_df[j,:] = var_mldD[j]

        var_psal_interp_df = var_psal_interp.flatten()
        var_temp_interp_df = var_temp_interp.flatten() 

        var_lon_df = var_lon_df.flatten() 
        var_lat_df = var_lat_df.flatten() 
        var_day_df = var_day_df.flatten()
        var_date_df = var_date_df.flatten() 
        var_dep_df = var_dep_df.flatten()
        var_mldT_df = var_mldT_df.flatten()
        var_mldD_df = var_mldD_df.flatten()

        #print(np.shape(var_name_df),np.shape(var_nbtim_df),np.shape(var_lat_df),np.shape(var_day_df),np.shape(var_psal_interp_df),np.shape(var_nbdep_df),np.shape(var_lon_df),np.shape(var_date_df),np.shape(var_dep_df))
        df_psal_temp_i = pd.DataFrame({"Argo": var_name_df, "Latitude": var_lat_df, "Longitude": var_lon_df, "Day": var_day_df, "Date": var_date_df, "Depth level": var_dep_df, "PSAL": var_psal_interp_df, "TEMP": var_temp_interp_df, "MldT": var_mldT_df, "MldD": var_mldD_df})      
        if index_file == 0:
            df_psal_temp = df_psal_temp_i
        else:
            df_psal_temp = pd.concat([df_psal_temp,df_psal_temp_i], ignore_index = True)        
    return df_psal_temp
    


def interp_psal_temp(nb_tim,nb_dep,gotm_dep,var_day,var_dep,var_psal,var_temp):
#----------------------------
# Compute PSAL & TEMP interpolation on standard depth levels, basically same operations as with CPHL interpolation but psal and temp data are not flattened yet
#----------------------------   
########
#     In :
#     nb_tim(int): number of timestamps for the Argo float
#     nb_dep(int): number of depth levels  
#     gotm_dep: 1D array of size nb_dep containing standard depth levels
#     var_day: 1D array of size nb_tim containing all timestamps in Julian days
#     var_dep: 2D array of size nb_tim * unknownsize containing depth levels where each CPHL was monitored
#     var_psal: 2D array of size nb_tim * unknownsize containing PSAL data
#     var_temp: 2D array of size nb_tim * unknownsize containing TEMP data

#     Out: 
#     var_date_df: 2D array of size nb_tim*nb_dep containing all recording dates with datetime format, every column of the array is filed with the same date value
#     var_psal_interp: 2D array of size nb_tim*nb_dep containing all PSAL data
#     var_temp_interp: 2D array of size nb_tim*nb_dep containing all TEMP data
########
    start=dt.datetime(1950,1,1,0,0,0)
    chunks_date=[]
    chunks_psal_interp=[]
    chunks_temp_interp=[]

    for j in range(nb_tim):
        delta=dt.timedelta(var_day[j])
        offset = delta + start
        date = np.array([offset for j in range(nb_dep)])
        chunks_date.append(date)
        var_psal_1d=var_psal[j,:]
        var_temp_1d=var_temp[j,:]
        var_dep_1d=var_dep[j,:]
        var_psal_1d_interp=np.interp(gotm_dep,var_dep_1d,var_psal_1d)
        var_temp_1d_interp=np.interp(gotm_dep,var_dep_1d,var_temp_1d)
        chunks_psal_interp.append(var_psal_1d_interp)
        chunks_temp_interp.append(var_temp_1d_interp)
        
    var_date_df = np.stack(chunks_date, axis=0)
    chunks_psal_interp = np.array(chunks_psal_interp,dtype='float')
    chunks_psal_interp[chunks_psal_interp <= 0] = np.nan
    chunks_temp_interp = np.array(chunks_temp_interp,dtype='float')
    chunks_temp_interp[chunks_temp_interp <= 0] = np.nan
    var_psal_interp=np.vstack(chunks_psal_interp)
    var_temp_interp=np.vstack(chunks_temp_interp)
    
    return var_date_df, var_psal_interp, var_temp_interp
    
    


def plot_profiles(df,variable,synchronize,save,directory_save,mld,depth_max):
#----------------------------
# Plot CPHL PSAL & TEMP profiles from a directory
#----------------------------    
########
#     In : 
#     df: Dataframe with variables to plot,
#     variable (str)       : Variable to plot, could be set as "CPHL", "CPHL Raw", "PSAL", "TEMP"
#     synchronize (boolean):
#     save (boolean)       : If true, save profiles display in directory save
#     directory_save       : folder where profiles will be saved
#     mld (boolean)        : If true, plot mldT & mldD time series
#     depth_max (int)      : Set maximal depth for profile display

#     Out: 
#     plot the profiles of the asked variable (one profile per float)
########
    floats = df["Argo"].unique()
    
    for index,Afloat in enumerate(floats):    
        id = Afloat
        df_i = df.loc[df["Argo"] == Afloat]  ### Select part of Dataframe that correspond to the Argo float we wanna plot ####
        fig = plt.figure(figsize=(10,4))
        ax = plt.subplot(111)

        depths = df_i["Depth level"].unique()
        nb_dep = len(depths) 
        dates = df_i["Date"].unique()
        nb_date = len(dates) 
        
        datemin = dates[0]
        datemax = dates[-1]
                   
        variable_array = df_i[[variable]].to_numpy()   
        variable_array = variable_array.reshape((nb_date,nb_dep))           
        xx, yy = np.meshgrid(dates,depths)

        if synchronize == True:
            title = id + "_" + variable + "_interpolated_synchronized_profile"
            ax.set_title(title)
        else:
            title = id +"_" + variable + "_interpolated_profile"
            ax.set_title(title)
                
        if variable == "PSAL":    
            cf = ax.pcolormesh(xx,yy,variable_array[:-1, :-1].T,cmap='rainbow',shading = "flat", vmin=34,vmax=36)
            cb = plt.colorbar(cf,orientation='vertical',extend='both')
            cb.set_label('Salinity [PSU]', rotation=270, labelpad=15.0)

        elif variable == "TEMP":
            cf = ax.pcolormesh(xx,yy,variable_array[:-1, :-1].T,cmap='coolwarm',shading = "flat", vmin=0,vmax=15)
            cb = plt.colorbar(cf,orientation='vertical',extend='both')
            cb.set_label("Temperature [°C]", rotation=270, labelpad=15.0)

        elif variable == "CPHL" or variable == "CPHL Raw":
            cf = ax.pcolormesh(xx,yy,np.log(variable_array[:-1, :-1].T),cmap='viridis',shading = "flat", vmin=-4,vmax=2)
            cb = plt.colorbar(cf,orientation='vertical',extend='both')
            cb.set_label("Chl [log(mg/m3)]", rotation=270, labelpad=15.0)

        if mld == True:

            mldT = df_i[["MldT"]].to_numpy()
            mldD = df_i[["MldD"]].to_numpy()
            mldT = mldT.reshape((nb_date,nb_dep))
            mldD = mldD.reshape((nb_date,nb_dep))

            mldT_1D = [mldT[i,0] for i in range(nb_date)]
            mldD_1D = [mldD[i,0] for i in range(nb_date)]

            ax.plot(dates, mldT_1D, color = "red", label = "MldT")
            ax.plot(dates, mldD_1D, color = "blue", label = "MldD")
            ax.legend()    
            plt.gca().invert_yaxis()   

        ax.invert_yaxis()
        ax.set_ylim([depth_max,0])
        ax.set_xlim([datemin,datemax])
        ax.set_ylabel('Depth [m]')
        ax.set_xlabel('Date [YYYY-MM]')
        dfmt = mdates.DateFormatter('%Y-%m')
        #lfmt = mdates.DayLocator(interval=3)
        lfmt = mdates.MonthLocator(interval=3)
        ax.xaxis.set_major_formatter(dfmt)
        ax.xaxis.set_major_locator(lfmt)
        fig.autofmt_xdate()
        fig.tight_layout()
        if save == True:
            fig.savefig(directory_save + title + ".png")



def plot_trajectories(directory):
# #----------------------------
# # draw Argo trajectories of netcdf files from a directory
# #----------------------------    
########
#     In : 
#     directory: Directory with nc files whose trajectories will be plotted
#
#     Out: 
#     plot
########    
    os.chdir(directory) 
    cwd = os.getcwd()
    dir_list = os.listdir(cwd)

        
    # Define a Cartopy 'ordinary' lat-lon coordinate reference system.
    crs_latlon = ccrs.PlateCarree()
    
    fig = plt.figure(figsize=(16,9))
    fig.suptitle("Trajectories of Argo floats in Norwegian sea")

    ax3 = fig.add_subplot(1, 2, 1, projection=ccrs.Orthographic(0, 90))
    ax3.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
    ax3.coastlines()
    ax3.stock_img()
    ax3.set_title("Large scale")

    ax4 = fig.add_subplot(1, 2, 2, projection=ccrs.Orthographic(0, 90))
    ax4.set_extent((-30,30,60,80), crs=crs_latlon)
    ax4.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
    ax4.coastlines()
    ax4.stock_img()
    ax4.set_title("Norwegian sea scale")


    for index, file in enumerate(dir_list):
        infile=directory+'/'+file

        if os.path.exists(infile):
            ncfile = open_netcdf(infile)
            var_lat_ma = ncfile.variables['LATITUDE'][:]        # [degree north]
            var_lon_ma = ncfile.variables['LONGITUDE'][:]       # [degree east]
        else:
            print('Can not find '+file+', EXIT')
            exit()
        ax3.plot(var_lon_ma,var_lat_ma,transform=crs_latlon)
        ax4.plot(var_lon_ma,var_lat_ma,transform=crs_latlon)

    


    
def synchronize(df_cphl,df_psal_temp):
# #----------------------------
# # Synchronize PSAL & TEMP data on CPHL data
# #----------------------------    
########
#     In : 
#     df_cphl: Dataframe with cphl data
#     df_psal_temp: dataframe with psal and temp data
#
#     Out: 
#     df_synchronized: Datafrmae with CPHL PSAL TEMP mldT mldD data synchronized on CPHL data
########
########
#     Global operation:
#     -For each Argo floats:
#     -Read each time stamps from CPHL data 
#     -Create a list of intervals for each CPHL timestamp, thus, create a 2D array of size 2*nb_tim, first column filled with day-10, second with day+10
#     -Then, for each PSAL/TEMP timestamp, check if the PSAL/TEMP timestamp is in one of the CPHL timestamp intervals created in previous step
#     -If true, add PSAL/TEMP/mldT/mldD values in a new "synchronized" array, with index synchronized on matching CPHL interval
########


    df_synchronized = df_cphl
    
    floats_id = df_psal_temp["Argo"].unique()
        
    psal_synchronized = []
    temp_synchronized = []
    mldT_synchronized = []
    mldD_synchronized = []
        
    for i in range(len(floats_id)):
        float_i = floats_id[i]
        df_cphl_i = df_cphl.loc[df_cphl["Argo"] == float_i]
        days_cphl_i = df_cphl_i["Day"].unique()
        len_days_cphl_i = np.shape(days_cphl_i)[0]
        depth_cphl_i = df_cphl_i["Depth level"].unique()
        len_depth_i = np.shape(depth_cphl_i)[0]
        
        df_psal_temp_i = df_psal_temp.loc[df_psal_temp["Argo"] == float_i]
        days_psal_temp_i = df_psal_temp_i["Day"].unique()
        len_days_psal_temp_i = np.shape(days_psal_temp_i)[0]
        psal_i = df_psal_temp_i["PSAL"].to_numpy()
        psal_i = np.reshape(psal_i, (len_days_psal_temp_i , len_depth_i))
        temp_i = df_psal_temp_i["TEMP"].to_numpy()
        temp_i = np.reshape(temp_i, (len_days_psal_temp_i , len_depth_i))
        mldT_i = df_psal_temp_i["MldT"].to_numpy()
        mldT_i = np.reshape(mldT_i, (len_days_psal_temp_i , len_depth_i))
        mldD_i = df_psal_temp_i["MldD"].to_numpy()
        mldD_i = np.reshape(mldD_i, (len_days_psal_temp_i , len_depth_i))
        
        psal_synchronized_i = np.empty((len_days_cphl_i , len_depth_i))
        psal_synchronized_i [:] = np.nan
        temp_synchronized_i = np.empty((len_days_cphl_i , len_depth_i))
        temp_synchronized_i [:] = np.nan
        mldT_synchronized_i = np.empty((len_days_cphl_i , len_depth_i))
        mldT_synchronized_i [:] = np.nan
        mldD_synchronized_i = np.empty((len_days_cphl_i , len_depth_i))
        mldD_synchronized_i [:] = np.nan
        
        intervals_cphl = np.zeros((len_days_cphl_i,2))
        
        for k in range(len_days_cphl_i):
            intervals_cphl[k][0],intervals_cphl[k][1] = days_cphl_i[k]-10, days_cphl_i[k]+10
        
        for j in range (len_days_psal_temp_i):
            for k in range(len_days_cphl_i):
                if intervals_cphl[k][0] < days_psal_temp_i[j] < intervals_cphl[k][1]:                    
                    psal_synchronized_i[k,:] = psal_i[j,:]
                    temp_synchronized_i[k,:] = temp_i[j,:]
                    mldT_synchronized_i[k,:] = mldT_i[j,:]
                    mldD_synchronized_i[k,:] = mldD_i[j,:]     
                        
        psal_synchronized.append(psal_synchronized_i.flatten())
        temp_synchronized.append(temp_synchronized_i.flatten())
        mldT_synchronized.append(mldT_synchronized_i.flatten())
        mldD_synchronized.append(mldD_synchronized_i.flatten())
        
    flat_list_psal = [item for sublist in psal_synchronized for item in sublist]
    flat_list_temp = [item for sublist in temp_synchronized for item in sublist]
    flat_list_mldT = [item for sublist in mldT_synchronized for item in sublist]
    flat_list_mldD = [item for sublist in mldD_synchronized for item in sublist]
    
    df_synchronized ["PSAL"] = flat_list_psal
    df_synchronized ["TEMP"] = flat_list_temp
    df_synchronized ["MldT"] = flat_list_mldT
    df_synchronized ["MldD"] = flat_list_mldD
            
            
    return df_synchronized
    
    
    
def get_mld(psal,temp,dep2D):
# #----------------------------
# # Compute mldT & mldD from PSAL and TEMP data
# #----------------------------    
########
#     In : 
#     psal: 2D array of size nb_tim*nb_dep containing Salinity data
#     temp: 2D array of size nb_tim*nb_dep containing Temperature data
#     dep2D: 2D array of size nb_tim*nb_dep containing Depth data
#
#     Out: 
#     mldT: 1D array of size nb_tim with mldT data for each date
#     mldD: 1D array of size nb_tim with mldD data for each date
########
########
#     Global operation:
#     -First, compute density for each PSAL/TEMP couple thanks to seawater library 
#     -Then, for each timestamp, compute mldT and mldD 
#     -mldT is computed by founding the smallest depth with at least 0.2°C gap between two consecutive temp values 
#     -mldD is computed by founding the smallest depth with at least 0.03 psu gap between two consecutive psal values
#     -These methods and constants come from many scientific papers and are commonly used to define mldT & mldD
########

    psal = psal.T
    temp = temp.T
    dep2D = dep2D.T
   
    t = T90conv(temp); s = psal
    dens = sw.pden(s, t, dep2D)
    
    mldT = np.zeros((t.shape[1]))
    mldD = np.zeros((t.shape[1]))
    
    ## replace nan by 0, otherwise, mld will suit on nan values
    t = np.where(np.isnan(t),0,t)
    dens = np.where(np.isnan(dens),0,dens)
    
   
    for day in range(t.shape[1]):
           pres10m_index = np.abs(dep2D[:,day] - 10.).argmin()
    #       if np.abs(dep2D[pres10m_index,day] - 10.) <= 2.:
           mldTindex = np.abs( t[:,day] - (t[pres10m_index,day] - 0.2) ).argmin()
           mldT[day] = dep2D[mldTindex,day]
           mldDindex = np.abs( dens[:,day] - (dens[pres10m_index,day] + 0.03) ).argmin()
           mldD[day] = dep2D[mldDindex,day]

  
    
    return mldT,mldD


def empty_low_quality_profiles(df,depth_max,max_missing_values):
# #----------------------------
# # Empty profiles with too little data in the surface depth layer
# #----------------------------    
########
#     In : 
#     df: Dataframe with all cphl profiles
#     depth_max (int): Defines the surface depth layer
#     max_missing_values (int): Maximum number of missing values in the surface depth layer to keep the profile
#
#     Out: 
#     df_final: Dataframe containing the cphl profiles, with Nan filled profiles if too little data in the surface depth layer
#     "CPHL Raw" is a new column corresponding to data before processing, it could be useful to have these data to check the impact of all processes
########
########
#     Global operation:
#     -For each timestamp of the Dataframe 
#     -Create a small Dataframe df_t containing only values for the running timestamp 
#     -Create an even smaller Dataframe df_t_surface containing values from surface layer, defined by depth_max variable 
#     -Then, check if there is more missing values than the maximum missing values we defined (max_missing_values)
#     -If True, fill the column with Nan and set keep empty as True
#     -If False, do nothing
#     -As low quality profile should not be filled by annual average profile, "Keep empty" is a new column of the dataframe used in next fonction to know if this profile should be filled or not
########

    floats = df["Argo"].unique()
    dates = df["Date"].unique()
    all_dates = df["Date"].to_numpy()
    depths = df["Depth level"].unique()
    nb_dep = len(depths)
    nb_tim = len(dates)
    
    index_depth = abs(depths - depth_max).argmin() 
    depth_to_check = depths[:index_depth] ## Only "depth_max" first meters
    
    for index, date in enumerate (dates):
        keep_empty = np.full(nb_dep, False)
        
        df_t = df.loc[df["Date"] == date]
        df_t = df_t.copy()
        df_t["CPHL Raw"] = df_t["CPHL"]
        
        df_t_surface = df_t[df_t["Depth level"].isin(depth_to_check)]
        nb_nan_surface = sum( np.isnan( df_t_surface["CPHL"].to_numpy() ))
        if nb_nan_surface > max_missing_values:
            df_t["CPHL"] = np.nan            
            keep_empty[:] = True
        
        var_name_df = np.full((nb_dep), df_t["Argo"].to_numpy()[0])
        var_lat_df, var_lon_df = np.full((nb_dep), df_t["Latitude"].to_numpy()[0]), np.full((nb_dep), df_t["Longitude"].to_numpy()[0])
        var_day_df, var_date_df = np.full((nb_dep), df_t["Day"].to_numpy()[0]), [date]*nb_dep
        var_dep_df = depths
        var_cphl_df = df_t["CPHL"].to_numpy()
        var_cphl_raw_df = df_t["CPHL Raw"].to_numpy()
        
        #print(np.shape(var_name_df),np.shape(var_lat_df),np.shape(var_day_df),np.shape(var_cphl_df),np.shape(var_lon_df),np.shape(var_date_df),np.shape(var_dep_df),np.shape(keep_empty))
        
        df_t = pd.DataFrame({"Argo": var_name_df, "Latitude": var_lat_df, "Longitude": var_lon_df, "Day": var_day_df, "Date": var_date_df, "Depth level": var_dep_df, "CPHL": var_cphl_df, "CPHL Raw": var_cphl_raw_df, "Keep empty": keep_empty})
        
        if index == 0:
            df_final = df_t
        else:
            df_final = pd.concat([df_final,df_t], ignore_index = True)
    
    return df_final



def average_profiles(df, average_window):
# #----------------------------
# # Compute average annual profile using all the profiles
# #----------------------------    
########
#     In : 
#     df: Dataframe with all cphl profiles
#     average_window: Temporal resolution of the average annual profile
#
#     Out: 
#     df_cphl_avg: Dataframe containing the average annual profile
########
########
#     Global operation:
#     -First, round every timestamp of cphl dataframe to rounded days defined by the average_window (if average window = 5, rounded days will be 0,5,10,.. for January 1st, January 7th, January 11th ...) 
#     -For each rounded day, compute the mean cphl profile
########

    plot = True  # Set True if you want to see the annual average profile
    floats = df["Argo"].unique()
    dates = df["Date"].unique()
    all_dates = df["Date"].to_numpy()
    depths = df["Depth level"].unique()
    nb_dep = len(depths)
    #all_dates = all_dates.timetuple().tm_yday
    df["Day of year"] = df["Date"].dt.day_of_year
    df["Day of year"] = (average_window * round(df["Day of year"] / average_window)).astype("int")
    df["Day of year"] = np.where(df["Day of year"] > 365 , 360, df["Day of year"])
    days_rounded = df["Day of year"].unique()
    days_rounded.sort()
    
    cphl_mean = []
    for index, day in enumerate(days_rounded):
        df_i = df[df["Day of year"] == day]
        mean = df_i.groupby("Depth level").mean()["CPHL"]
        cphl_mean.append(mean)
    cphl_mean = np.array(cphl_mean)
    nb_tim = len(days_rounded)
    
    if plot == True:
        xx,yy = np.meshgrid(days_rounded,depths)
        fig = plt.figure(figsize=(10,4))
        ax = plt.subplot(111)
        cf = ax.pcolormesh(xx,yy,np.log(cphl_mean.T),cmap='viridis',shading = "auto", vmin=-4,vmax=2)
        ax.set_title("Average annual profile")
        ax.set_ylabel('Depth [m]')
        ax.set_xlabel('Day of year')
        ax.invert_yaxis()
        cb = plt.colorbar(cf,orientation='vertical',extend='both')
        cb.set_label("Chl [log(mg/m3)]", rotation=270, labelpad=15.0)
    
    var_day_df = np.zeros((nb_tim,nb_dep))	
    for j in range(nb_tim):
        var_day_df[j,:] = days_rounded[j] 
    var_day_df = var_day_df.flatten()
    cphl_mean_df = cphl_mean.flatten()
    var_dep_df = np.resize(depths, nb_tim*nb_dep) 
    
    df_cphl_avg = pd.DataFrame({"Day of year rounded": var_day_df,"Depth level": var_dep_df, "CPHL avg": cphl_mean_df}) 
    return df_cphl_avg     

    
    
    
    
def fill_gap(df_cphl, df_cphl_avg, average_window):
# #----------------------------
# # Fill missing values of a cphl profile with the average annual profile
# # Let Nan values if the profile is classified as low quality profile (Keep empty == True)
# #----------------------------    
########
#     In : 
#     df_cphl: Dataframe with cphl profiles to fill
#     df_cphl_avg: Dataframe containing the average annual profile
#     average_window: Temporal resolution of the average annual profile
#
#     Out: 
#     df_cphl: Dataframe with cphl profiles filled with average annual profile, but with nan values if low quality profile
########
########
#     Global operation:
#     -First, round every timestamp of cphl dataframe to rounded days defined by the average_window (if average window = 5, rounded days will be 0,5,10,.. for January 1st, January 7th, January 11th ...) 
#     -Find the index of every Nan value in cphl data
#     -For every Nan value index, replace the Nan by the matching CPHL annual average value, with matching depths and rounded date
#     -If "Keep empty" is True, let Nan values as this profile is a low quality one
########

    df_cphl["Day of year rounded"] = df_cphl["Date"].dt.day_of_year
    df_cphl["Day of year rounded"] = (average_window * round(df_cphl["Day of year rounded"] / average_window)).astype("int")
    df_cphl["Day of year rounded"] = np.where(df_cphl["Day of year rounded"] > 365 , 360, df_cphl["Day of year rounded"])
    
    list_index_nan = df_cphl['CPHL'].index[df_cphl['CPHL'].apply(np.isnan)]

    for index in list_index_nan:
        index_cphl_avg = df_cphl_avg.index[(df_cphl_avg["Day of year rounded"] == df_cphl["Day of year rounded"][index]) & (df_cphl_avg["Depth level"] == df_cphl["Depth level"][index])]
        df_cphl.loc[index, "CPHL"] = df_cphl_avg.at[index_cphl_avg[0], "CPHL avg"]
        
    df_cphl.loc[df_cphl["Keep empty"] == True, "CPHL"]  = np.nan

    return df_cphl
    
    
    
    
    
def scatter_plot(df,mode):
    
    cphl = df["CPHL"]
    depth = df["Depth level"]
    
    fig = plt.figure(figsize=(10,4))
    ax = plt.subplot(111)
    cf = ax.scatter(cphl,depth)
    ax.set_title("Scatter plot for {} mode".format(mode))
    ax.set_ylabel('Depth [m]')
    ax.set_xlabel('Chl [log(mg/m3)]')
    ax.set_xlim(-0.1,5)
    
    
    
    
    
    

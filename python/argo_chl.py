from netCDF4 import Dataset as NetCDFFile
import numpy as np
import os,fnmatch
import datetime
import pickle


directory = '/cluster/work/users/cagyum/BIOARGO/'
nargo = np.size(sorted(fnmatch.filter(os.listdir(directory), '*.nc')))

DATA = {'EACH':{},
        'ALL': {'lat': -999., 'lon': -999., 'year': -999., 'day': -999.,  'time': -999., 'depth': -999., 'chl': -999.} }
for item in range(nargo):
  DATA['EACH'][item] =  {'lat': -999., 'lon': -999., 'year': -999., 'day': -999.,  'time': -999., 'depth': -999., 'chl': -999.,'name': -999.}

argocount=0
for f1 in sorted(fnmatch.filter(os.listdir(directory), '*.nc')):
  print(f1)
  nc = NetCDFFile(directory+f1)

  pres    = nc.variables['PRES'][:,:]
  presqc  = nc.variables['PRES_QC'][:,:]
  chl     = nc.variables['CPHL_ADJUSTED'][:,:]
  chlqc   = nc.variables['CPHL_ADJUSTED_QC'][:,:]
  time    = nc.variables['TIME'][:]
  lon     = nc.variables['LONGITUDE'][:]
  lat     = nc.variables['LATITUDE'][:]

  timelimit = 25012 # 2018 end of june, satellite L4 does not exist from this day on
  if np.size( pres[time<=timelimit] ) > 0:
  
   pres   = pres[time<=timelimit]
   presqc = presqc[time<=timelimit]
   chl    = chl[time<=timelimit]
   chlqc  = chlqc[time<=timelimit]
   lon    = lon[time<=timelimit]
   lat    = lat[time<=timelimit]
   time   = time[time<=timelimit]

#   pres = np.ma.masked_where( presqc>2, pres )
#   pres = np.ma.masked_where( presqc==0, pres )
#   chl  = np.ma.masked_where( chlqc>2, chl )
#   chl  = np.ma.masked_where( chlqc==0, chl )
#   chl  = np.ma.masked_where(chl < 0.0, chl)

   pres = np.ma.masked_where( (presqc==0),pres)
   pres = np.ma.masked_where( (presqc==3),pres)
   pres = np.ma.masked_where( (presqc==4),pres)
   pres = np.ma.masked_where( (presqc==6),pres)
   pres = np.ma.masked_where( (presqc==7),pres)
   pres = np.ma.masked_where( (presqc==8),pres) 
   pres = np.ma.masked_where( (presqc==9),pres)

   chl  = np.ma.masked_where( (chlqc==0), chl)
   chl  = np.ma.masked_where( (chlqc==3), chl)
   chl  = np.ma.masked_where( (chlqc==4), chl)
   chl  = np.ma.masked_where( (chlqc==6), chl)
   chl  = np.ma.masked_where( (chlqc==7), chl)
   chl  = np.ma.masked_where( (chlqc==8), chl) 
   chl  = np.ma.masked_where( (chlqc==9), chl)
   

   msk = (~pres.mask & ~chl.mask)
   lat2d = np.ones((pres.shape))
   lon2d = np.ones((pres.shape))
   time2d= np.ones((pres.shape))   

   for i in range(0,pres.shape[0]):
       for j in range(0,pres.shape[1]):
           time2d[i,j] = time[i]
           lat2d[i,j]  = lat[i]
           lon2d[i,j]  = lon[i]

   chl1d = chl[msk]
   prs1d = pres[msk]
   time1d= time2d[msk]
   lat1d = lat2d[msk]
   lon1d = lon2d[msk]

   yrall = np.zeros(time1d.shape[0])
   dayall = np.zeros(time1d.shape[0])
   dateall = []

   yralleach = np.zeros(time.shape[0])
   dayalleach = np.zeros(time.shape[0])
   datealleach = []

   for j in range(0,time1d.shape[0]):
       a = datetime.datetime(1950, 1, 1, 0, 0) + datetime.timedelta(time1d[j])
       yrall[j] = a.strftime('%Y')
       dayall[j] = a.strftime('%j')

   for j in range(time1d.shape[0]):
       a = datetime.datetime(1950, 1, 1, 0, 0) + datetime.timedelta(time1d[j])
       dateall.append(a.strftime('%Y%b%d'))

   for j in range(0,time.shape[0]):
       a = datetime.datetime(1950, 1, 1, 0, 0) + datetime.timedelta(time[j])
       yralleach[j] = a.strftime('%Y')
       dayalleach[j] = a.strftime('%j')

   for j in range(time.shape[0]):
       a = datetime.datetime(1950, 1, 1, 0, 0) + datetime.timedelta(time[j])
       datealleach.append(a.strftime('%Y%b%d'))

   DATA['EACH'][argocount]['lat']   = lat
   DATA['EACH'][argocount]['lon']   = lon
   DATA['EACH'][argocount]['year']  = yralleach
   DATA['EACH'][argocount]['day']   = dayalleach
   DATA['EACH'][argocount]['time']  = time
   DATA['EACH'][argocount]['depth'] = pres
   DATA['EACH'][argocount]['chl']   = chl
   DATA['EACH'][argocount]['name']  = f1

   DATA['ALL']['lat']   = np.concatenate( (DATA['ALL']['lat'],lat1d), axis = None )
   DATA['ALL']['lon']   = np.concatenate( (DATA['ALL']['lon'],lon1d), axis = None )
   DATA['ALL']['year']  = np.concatenate( (DATA['ALL']['year'],yrall), axis = None )
   DATA['ALL']['day']   = np.concatenate( (DATA['ALL']['day'],dayall), axis = None )
   DATA['ALL']['time']  = np.concatenate( (DATA['ALL']['time'],time1d), axis = None )
   DATA['ALL']['depth'] = np.concatenate( (DATA['ALL']['depth'],prs1d), axis = None )
   DATA['ALL']['chl']   = np.concatenate( (DATA['ALL']['chl'],chl1d), axis = None )

   argocount = argocount + 1
  nc.close()
  

DATA['ALL']['lat']   = DATA['ALL']['lat'][1:]
DATA['ALL']['lon']   = DATA['ALL']['lon'][1:]
DATA['ALL']['year']  = DATA['ALL']['year'][1:]
DATA['ALL']['day']   = DATA['ALL']['day'][1:]
DATA['ALL']['time']  = DATA['ALL']['time'][1:]
DATA['ALL']['depth'] = DATA['ALL']['depth'][1:]
DATA['ALL']['chl']   = DATA['ALL']['chl'][1:]

for item in reversed(range(len(DATA['EACH']))):
  if np.size(DATA['EACH'][item]['lat'])== 1:
    if DATA['EACH'][item]['lat']== -999.:
     del DATA['EACH'][item]

f = open(directory+'argodata','wb')
pickle.dump(DATA,f)
f.close()
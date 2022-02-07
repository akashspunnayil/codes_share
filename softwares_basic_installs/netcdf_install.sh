
# https://cloud-gc.readthedocs.io/en/stable/chapter04_developer-guide/install-basic.html
#https://www.unidata.ucar.edu/software/netcdf/docs/getting_and_building_netcdf.html
# First install netcdf-c , then netcdf-fortran separately
#
# Install netcdf librabries
sudo apt-get install libnetcdf-dev libnetcdff-dev

# Check NetCDF-C configuration: paths and other details
nc-config --all

# Check NetCDF-Fortran configuration: flibs paths and other details
nf-config --all

# TEST netcdf
wget https://www.unidata.ucar.edu/software/netcdf/examples/programs/simple_xy_wr.f90
gfortran simple_xy_wr.f90 -o test_nc.exe -I/usr/include -lnetcdff
./test_nc.exe
# *** SUCCESS writing example file simple_xy.nc!

# Install ncdump to check data content:
sudo apt install netcdf-bin
ncdump -h simple_xy.nc


# INSTALLING netCDF-C
# For netCDF-4 support: HDF5 1.8.9 or later. HDF5 1.10.1 or later.
# zlib 1.2.5 or later (for netCDF-4 compression)
# curl 7.18.0 or later (for DAP remote access client support)
# For parallel I/O support on classic netCDF files:PnetCDF 1.6.0 or later
# Versions required are at least HDF5 1.8.9, zlib 1.2.5, and curl 7.18.0 or later.

#Important Note: When building netCDF-C library versions older than 4.4.1, use only HDF5 1.8.x #versions. 

# /usr/include, /usr/lib/x86_64-linux-gnu
# Build and install zlib
tar xvfz zlib-1.2.11.tar.gz
ZDIR=/usr
sudo ./configure --prefix=${ZDIR}
sudo make check
sudo make install   # or sudo make install, if root permissions required
#
# Build and install HDF5
ZDIR=/usr
H5DIR=/usr
sudo ./configure --with-zlib=${ZDIR} --prefix=${H5DIR} --enable-hl
sudo make check
sudo make install   # or sudo make install, if root permissions required

# Build and install netCDF-4
ZDIR=/usr
H5DIR=/usr
NCDIR=/usr
CPPFLAGS='-I${H5DIR}/include -I${ZDIR}/include' LDFLAGS='-L${H5DIR}/lib -L${ZDIR}/lib' sudo ./configure --prefix=${NCDIR}
sudo make check
sudo make install  # or sudo make install

# Build and install HDF4: HDF5 must be installed before this
H4DIR=/usr
sudo ./configure --enable-shared --disable-netcdf --disable-fortran --prefix=${H4DIR}
sudo make check
sudo make install

# Then from the top-level netCDF directory:
# Build and install netCDF-4 with HDF4 access enabled
H5DIR=/usr
H4DIR=/usr
CPPFLAGS="-I${H5DIR}/include -I${H4DIR}/include" \
  LDFLAGS="-L${H5DIR}/lib -L${H4DIR}/lib" \
  sudo ./configure --enable-hdf4 --enable-hdf4-file-tests
sudo make check
sudo make install

# Building with Parallel I/O Support
# Build and install HDF5 with parallel support
H5DIR=/usr
CC=mpicc sudo ./configure --enable-parallel --prefix=${H5DIR}
sudo make check
sudo make install

# Build, test, and install netCDF-4 with HDF5 parallel support
H5DIR=/usr
NCDIR=/usr
CC=mpicc CPPFLAGS=-I${H5DIR}/include LDFLAGS=-L${H5DIR}/lib \
  sudo ./configure --disable-shared --enable-parallel-tests --prefix=${NCDIR}
sudo make check
sudo make install

# Building PnetCDF from source
# To enable parallel I/O support for classic netCDF files, i.e. CDF-1, 2 and 5 formats, PnetCDF library must also be installed. 
# Build and install PnetCDF
#PNDIR=/usr
#sudo ./configure --prefix=${PNDIR} --with-mpi=/path/to/MPI/compilers
#sudo make check
#sudo make install   # or sudo make install, if root permissions required

# Build, test, and install netCDF-4 with PnetCDF support
H5DIR=/usr
NCDIR=/usr
PNDIR=/usr
CC=mpicc CPPFLAGS="-I${H5DIR}/include -I${PNDIR}/include" \
  LDFLAGS="-L${H5DIR}/lib -L${PNDIR}/lib" sudo ./configure \
  --enable-pnetcdf  --enable-parallel-tests \
  --prefix=${NCDIR}
sudo make check
sudo make install

# Linking to netCDF-C
ZDIR=/usr
H5DIR=/usr
NCDIR=/usr
PNDIR=/usr
LIBS="-L${NCDIR}/lib -lnetcdf -L${H5DIR}/lib -lhdf5_hl -lhdf5 -L${PNDIR} -lpnetcdf -L${ZDIR}/lib -lz -lm"

#PKG_CONFIG_PATH=${NCDIR}/lib/pkgconfig:$PKG_CONFIG_PATH
#export PKG_CONFIG_PATH
#cc -o myapp myapp.c `pkg-config --cflags --libs netcdf`


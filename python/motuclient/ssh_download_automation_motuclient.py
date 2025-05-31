import os
from datetime import datetime, timedelta

start_date = datetime(2002, 1, 1)
end_date = datetime(2020, 12, 31)

delta_t = timedelta(days=365)  # 1 year --- if Our requested data is daily eg: cmems_obs-sl_glo_phy-ssh_my_allsat-l4-duacs-0.25deg_P1D
#delta_t = timedelta(days=13)   # 1 year --- if Our requested data is monthly eg: cmems_mod_arc_phy_my_topaz4_P1D-m

serviceID = "SEALEVEL_GLO_PHY_L4_MY_008_047"
productID = "cmems_obs-sl_glo_phy-ssh_my_allsat-l4-duacs-0.25deg_P1D"
lon = [40, 100]
lat = [0, 30]
var = "--variable adt --variable sla --variable ugos --variable ugosa --variable vgos --variable vgosa"

out_dir = "./"
USERNAME = "asomasekharan1"
PASSWORD = "123Ak123@"

# Download loop
while start_date <= end_date:
    # Output filename
    out_name = f"cmems_obs_sl_glo_phy_ssh_my_allsat_l4_duacs_0.25deg_P1D_{start_date.year}.nc"

    if start_date.month == 1:
        # Motuclient command line
        query = f'python -m motuclient --motu https://my.cmems-du.eu/motu-web/Motu \
        --service-id {serviceID}-TDS --product-id {productID} \
        --longitude-min {lon[0]} --longitude-max {lon[1]} --latitude-min {lat[0]} --latitude-max {lat[1]} \
        --date-min "{start_date}" --date-max "{start_date+delta_t}" \
        {var} \
        --out-dir {out_dir} --out-name {out_name} --user {USERNAME} --pwd {PASSWORD}'

        print(f"============== Running request on {start_date} ==============")
        print(query[:-30])

        # Run the command
        os.system(query)

    start_date = start_date.replace(year=start_date.year + 1)

print(f"============== Download completed! All files are in your directory {out_dir} ==============")


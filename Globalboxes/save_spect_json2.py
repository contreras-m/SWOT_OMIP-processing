
from datetime import datetime
import s3fs
import xarray as xr
import pyinterp
from widetrax import DataPreprocessing as dp
from widetrax import Spectra as sp
import numpy as np
import json
from watermark import watermark
import time
import platform

def save_spect(name_region,model_name,season,freq_mean,psd_mean,lon_min,lon_max,lat_min,lat_max,start_date,end_date):
    # Infos
    nom_region = name_region
    model = model_name
    name_season = season
    freqs_mean = np.array(freq_mean)
    psd_mean = np.array(psd_mean)
    todays_Date = datetime.now()
    date_creation = todays_Date.isoformat() #ISO 8601 format
    packages_versions = watermark(packages="numpy,widetrax,xarray,s3fs,pyinterp,datetime,json,platform,time")
    machine_info = {
        "system": platform.system(),
        "node_name": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version()
    }

    # JSON file structure
    donnees = {
        "region": nom_region,
        "model": model,
        "lon_min": lon_min,
        "lon_max": lon_max,
        "lat_min": lat_min,
        "lat_max": lat_max,
        "start_date": datetime.strptime(start_date, "%d%m%Y").strftime("%Y-%m-%d"),
        "end_date": datetime.strptime(end_date, "%d%m%Y").strftime("%Y-%m-%d"),
        "packages_versions": packages_versions,
        "date_creation": date_creation,
        "login_creator": platform.node(),
        "Frequency": freqs_mean.tolist(),
        "Spectra": psd_mean.tolist(),
        "machine_info": machine_info
    }

    # Save on JSON file
    with open(str(nom_region)+"_"+str(name_season)+"_"+str(model)+".json", "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=4)
#with open("OMIP_"+str(model)+"_"+str(nom_region)+"_"+str(name_season)+".json", "w", encoding="utf-8") as f:
  #  json.dump(donnees, f, ensure_ascii=False, indent=4)

#<region>-<period>-<data-source>.json
    print("JSON file created")
    return
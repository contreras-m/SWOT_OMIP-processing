#import plot_ration_psdglobal as ppR

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
from shapely.geometry import shape, box

def season_cum(models,selected,wlmin,wlmax,north_boxes,south_boxes):

    box=0
    psdsW=np.zeros((len(selected),5))
    psdsS=np.zeros((len(selected),5))

    for i, poly in enumerate(selected):

        if (i!=14) and (i!=15):
            season="JFM"
            spectrumJFM=[]
            freqJFM=[]
            # Plot spectrum JFM
            for imod in ["GLO12V4","GLO36V1","NOC12","NOC025","SWOT"]:
                filename = "GLOBALv2/" + imod +  "/Global_box_" + str(box) + "_" + season + "_" + imod + ".json"
                with open(filename, "r") as f:
                    data = json.load(f)
                spectrumJFM.append(data["Spectra"])
                freqJFM.append(data["Frequency"])

            season="JAS"
            spectrumJAS=[]
            freqJAS=[]
            # Plot spectrum JAS
            for imod in ["GLO12V4","GLO36V1","NOC12","NOC025","SWOT"]:
                filename = "GLOBALv2/" + imod +  "/Global_box_" + str(box) + "_" + season + "_" + imod + ".json"
                with open(filename, "r") as f:
                    data = json.load(f)
                spectrumJAS.append(data["Spectra"])
                freqJAS.append(data["Frequency"])


            wavelength=1/np.array(freqJFM)
 
            for imodel in range(len(models)): 
                poswl=np.where((wavelength[imodel]>wlmin) & (wavelength[imodel]<wlmax))
                spectrumJFMM=np.array(spectrumJFM[imodel])
                spectrumJASM=np.array(spectrumJAS[imodel])
                freqJASM = np.array(freqJAS[imodel])   # now it's a 2D array
                dk = np.gradient(freqJASM[poswl[0]])
                if box in north_boxes:
                    psdsW[box,imodel]  = np.cumsum(spectrumJFMM[poswl[0]] * dk)[-1]
                    psdsS[box,imodel]  = np.cumsum(spectrumJASM[poswl[0]] * dk)[-1]
                elif box in south_boxes:
                    psdsW[box,imodel]  = np.cumsum(spectrumJASM[poswl[0]] * dk)[-1]
                    psdsS[box,imodel]  = np.cumsum(spectrumJFMM[poswl[0]] * dk)[-1]
            box=box+1
        else:
            box=box+1


    return psdsW, psdsS,freqJAS


    
def cum_sum(psdsW,psdsS):
    with open("mostly_ocean_boxes_filtered.geojson") as f:
        data = json.load(f)

    nboxes = len(data["features"])
    
    lon_min_list = []
    lat_min_list = []

    for feature in data["features"]:
        coords = feature["geometry"]["coordinates"][0]
        lons = [pt[0] for pt in coords]
        lats = [pt[1] for pt in coords]

        lon_min_list.append(min(lons))
        lat_min_list.append(min(lats))

    lon_min_list = np.array(lon_min_list)
    lat_min_list = np.array(lat_min_list)

    lon_edges = np.arange(-180, 181, 10)
    lat_edges = np.arange(-90, 91, 10)

    nlon = len(lon_edges) - 1
    nlat = len(lat_edges) - 1

    ZW = np.full((5,nlat, nlon), np.nan)
    values = np.array(psdsW)   # shape (280,)
    for i in range(nboxes):
        lon_idx = np.where(lon_edges[:-1] == lon_min_list[i])[0][0]
        lat_idx = np.where(lat_edges[:-1] == lat_min_list[i])[0][0]
        for imodel in range(5):
            ZW[imodel,lat_idx, lon_idx] = np.array(values[i,imodel])

    ZS = np.full((5,nlat, nlon), np.nan)
    values = np.array(psdsS)   # shape (280,)
    for i in range(nboxes):
        lon_idx = np.where(lon_edges[:-1] == lon_min_list[i])[0][0]
        lat_idx = np.where(lat_edges[:-1] == lat_min_list[i])[0][0]
        for imodel in range(5):
            ZS[imodel,lat_idx, lon_idx] = np.array(values[i,imodel])

    return ZW, ZS
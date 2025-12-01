import os
import rasterio
import geopandas as gpd
import numpy as np
from rasterio.mask import mask
from shapely.geometry import mapping
import pandas as pd

# === Paths ===
root_dir = "sunshine/2011" # folder containing 01,02,...,12
provinces_file = "cn.json"

# === Load provinces ===
provinces = gpd.read_file(provinces_file)

# === Results storage ===
results = []

# === Loop over months ===
months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
for month_folder in months:
    month_path = os.path.join(root_dir, month_folder)
    raster_file = os.path.join(month_path, "w001001.adf")
    if not os.path.exists(raster_file):
        continue

    with rasterio.open(raster_file) as src:
        raster_crs = src.crs
        nodata = src.nodata if src.nodata is not None else -32768

        # Reproject provinces
        provinces_reproj = provinces.to_crs(raster_crs)

        for idx, province in provinces_reproj.iterrows():
            name = provinces.loc[idx, "name"]
            geom = [mapping(province.geometry)]
            try:
                out_image, out_transform = mask(src, geom, crop=True)
                data = out_image[0].astype(np.float32)
                data[data == nodata] = np.nan

                # Fix signed wraparound only for valid pixels
                mask_valid = ~np.isnan(data)
                data[mask_valid & (data < 0)] += 65536

                mean_val = float(np.nanmean(data))

                results.append({
                    "province": name,
                    "year": "2011",
                    "month": month_folder,
                    "mean_sunshine": mean_val
                })

            except Exception as e:
                print(f"{name}, {month_folder}: ERROR -> {e}")
                results.append({
                    "province": name,
                    "year": "2011",
                    "month": month_folder,
                    "mean_sunshine": np.nan
                })

# === Save results ===
df = pd.DataFrame(results)
#df1 = pd.read_csv("province_monthly_sunshine.csv")
df.to_csv("province_monthly_sunshine.csv", mode='a',header = False, index=False)
print("✅ Done! Results saved to province_monthly_sunshine.csv")


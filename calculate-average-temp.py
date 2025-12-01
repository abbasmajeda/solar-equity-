import xarray as xr
import geopandas as gpd
import rioxarray
import pandas as pd
import os

# -----------------------------
# User settings
# -----------------------------
nc_file = "tmp_2004.nc" # Path to your NetCDF file
province_file = "cn.json" # Path to your GeoJSON or Shapefile
temp_var = "tmp" # Replace with your NetCDF temperature variable name
output_file = "province_monthly_avg_temp.csv"

# -----------------------------
# Step 1: Load NetCDF lazily
# -----------------------------
print("Loading NetCDF file...")
ds = xr.open_dataset(nc_file, chunks={"time": 1}) # lazy loading
temp = ds[temp_var]

# Ensure spatial coordinates are named x/y for rioxarray
if "lat" in temp.coords:
    temp = temp.rename({"lat": "y"})
if "lon" in temp.coords:
    temp = temp.rename({"lon": "x"})

temp = temp.rio.write_crs("EPSG:4326") # assign CRS

# -----------------------------
# Step 2: Load provinces
# -----------------------------
print("Loading provinces...")
provinces = gpd.read_file(province_file)

# Ensure CRS matches temperature dataset
if provinces.crs is None:
    provinces = provinces.set_crs("EPSG:4326")
else:
    provinces = provinces.to_crs(temp.rio.crs)

# Remove existing output CSV if exists
if os.path.exists(output_file):
    os.remove(output_file)

# -----------------------------
# Step 3: Process one province and one month at a time
# -----------------------------
for i, province in provinces.iterrows():
    name = province["name"] # adjust if column name is different
    geom = [province.geometry]
    monthly_values = []

    for month in range(1, 13):
        # Select time for the month
        temp_month = temp.sel(time=temp['time'] == month)

        # Clip to province
        clipped = temp_month.rio.clip(geom, provinces.crs, drop=True)

        # Compute average safely
        avg = clipped.mean(dim=["x", "y", "time"]).compute().item()
        monthly_values.append(avg)

    # Save results immediately
    df = pd.DataFrame({
        "province": [name],
        "Month_1": [monthly_values[0]],
        "Month_2": [monthly_values[1]],
        "Month_3": [monthly_values[2]],
        "Month_4": [monthly_values[3]],
        "Month_5": [monthly_values[4]],
        "Month_6": [monthly_values[5]],
        "Month_7": [monthly_values[6]],
        "Month_8": [monthly_values[7]],
        "Month_9": [monthly_values[8]],
        "Month_10": [monthly_values[9]],
        "Month_11": [monthly_values[10]],
        "Month_12": [monthly_values[11]],
    })
    
    # Append to CSV
    df.to_csv(output_file, mode="a", index=False, header=not os.path.exists(output_file))
    print(f"✅ Finished {name}")

print(f" All provinces processed! Results saved to {output_file}")

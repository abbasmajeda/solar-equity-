import pandas as pd
import geopandas as gpd
import matplotlib
#matplotlib.use('Agg') # headless plotting
import matplotlib.pyplot as plt

# ---------- LOAD MONTHLY SII ----------
df = pd.read_csv('monthly_sii_per_province.csv')
df1 = pd.DataFrame()
df1['province'] = df['province'].str.strip()

# Month columns
month_cols = [f'month_{i}' for i in range(1,13)]
sii_months = df[month_cols]

# ---------- ANNUAL AVERAGE ----------
df1['Annual'] = sii_months.mean(axis=1, skipna=True)

# ---------- SEASONAL AVERAGES ----------
season_months = {
    'Spring': ['month_3','month_4','month_5'],
    'Summer': ['month_6','month_7','month_8'],
    'Autumn': ['month_9','month_10','month_11'],
    'Winter': ['month_12','month_1','month_2']
}

for season, cols in season_months.items():
    valid_cols = [c for c in cols if c in sii_months.columns]
    df1[season] = sii_months[valid_cols].mean(axis=1, skipna=True)

# ---------- SAVE COMBINED CSV ----------
df1.to_csv('sii_annual_seasonal_per_province.csv', index=False)
print("Saved annual & seasonal SII CSV")
print(df1.head())

# ---------- LOAD GEOJSON ----------
gdf = gpd.read_file("cn.json")

# ---------- PLOT MAPS ----------

name_map = {

   "内蒙古自治区": "Inner Mongolia",
   "西藏自治区": "Tibet",
  "宁夏回族自治区": "Ningxia",
   "广西壮族自治区": "Guangxi",
   "重庆市": "Chongqing",
   "Hong Kong": "Hong Kong", # include if in your GeoJSON/data
   "Macau": "Macao", # include if in your GeoJSON/data
   "北京市":"Beijing",
   "天津市":"Tianjin",
   "河北省":"Hebei",
   "山西省":"Shanxi",
   "辽宁省":"Liaoning",
   "吉林省":"Jilin",
   "黑龙江省":"Heilongjiang",
   "上海市":"Shanghai",
   "江苏省":"Jiangsu",
   "浙江省":"Zhejiang",
   "安徽省":"Anhui",
   "福建省":"Fujian",
   "江西省":"Jiangxi",
   "山东省":"Shandong",
   "河南省":"Henan",
   "湖北省":"Hubei",
   "湖南省":"Hunan",
   "广东省":"Guangdong",
   "海南省":"Hainan",
   "四川省":"Sichuan",
   "贵州省":"Guizhou",
   "云南省":"Yunnan",
   "陕西省":"Shaanxi",
   "甘肃省 ":"Gansu",
   "青海省":"Qinghai",
   "新疆维吾尔自治区":"Xinjiang"
    # Add/adjust others if your GeoJSON uses variants (e.g., "Hebei Sheng")
}


df1["province"] = df1["province"].replace(name_map).fillna(df1["province"])

plot_columns = ['Annual', 'Spring', 'Summer', 'Autumn', 'Winter']
for col in plot_columns:
    china_map = gdf.merge(df1, left_on= 'name', right_on='province', how='left')
    fig, ax = plt.subplots(1,1,figsize=(10,8))
    china_map.plot(column=col, cmap='YlOrRd', linewidth=0.8, edgecolor='black',
                   legend=True, legend_kwds={'label': f"{col} SII (0–100)"}, ax=ax)
    ax.set_title(f"{col} Solar Richness Index by Province", fontsize=14)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(f"{col.lower()}_sii.png", dpi=300)

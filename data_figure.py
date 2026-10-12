import sqlite3

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

conn = sqlite3.connect(r"F:\soil_data_reporting\soil_engine.sqlite")

df = pd.read_sql_query('''SELECT
    ph.sample_number,
    ph.sample_point_id,
    ph.depth_increment,

    -- pH and EC
    ph.pH,
    ph.EC,
    ph.EC_unit,

    -- Carbon
    c.LECO_TC_percent AS TC_percent,
    c.LECO_TC_gkg AS TC_gkg,
    c.LECO_OC_percent AS TOC_percent,
    c.LECO_OC_gkg AS TOC_gkg,

    -- Nitrogen
    n.TN_percent,

    -- Bulk density measurements
    bd.depth_upper,
    bd.depth_lower,
    bd.sample_wet_weight,
    bd.tin_weight,
    bd.tin_soil_wet_weight,
    bd.tin_soil_dry_weight,
    bd.core_diameter,
    bd.bag_weight,
    bd.coarse_fragment_weight,

    -- Texture
    t.sand_percent,
    t.silt_percent,
    t.clay_percent,
    t.texture_class

FROM ph_ec AS ph

LEFT JOIN carbon AS c
    ON ph.sample_number = c.sample_number

LEFT JOIN nitrogen AS n
    ON ph.sample_number = n.sample_number

LEFT JOIN bulk_density AS bd
    ON ph.sample_number = bd.sample_number

LEFT JOIN texture AS t
    ON ph.sample_number = t.sample_number''', conn)

conn.close()

print(df.head())

variables = [
    "pH",
    "EC",
    "TC_percent",
    "TOC_percent",
    "TN_percent",
    ("sand_percent",
    "silt_percent",
    "clay_percent")
]
variables_display = {
    "pH":"pH",
    "EC":"Electrical Conductivity",
    "TC_percent":"Total Carbon (%)",
    "TOC_percent":"Total Organic Carbon (%)",
    "TN_percent":"Total Nitrogen (%)",
    ("sand_percent",
    "silt_percent",
    "clay_percent"):"Soil Texture (%)",
"sand_percent":"Sand",
    "silt_percent":"Silt",
    "clay_percent":"Clay"
}

variables_display_1 = {
    "pH":"pH",
    "EC":"Electrical Conductivity",
    "TC_percent":"Total Carbon (%)",
    "TOC_percent":"Total Organic Carbon (%)",
    "TN_percent":"Total Nitrogen (%)",
"sand_percent":"Sand (%)",
    "silt_percent":"Silt (%)",
    "clay_percent":"Clay (%)"
}
df_old = df.copy(deep=True)
fig,axes = plt.subplots(nrows =2,ncols=3, figsize=(12, 10))


def remove_outliers_zscore(df, column_name, threshold=3):
    df_clean = df.copy()
    z_scores = (df_clean[column_name] - df_clean[column_name].mean()).abs() / df_clean[column_name].std()

    # Keep values where z_score < threshold, otherwise make them NaN
    df_clean[column_name] = df_clean[column_name].where(z_scores < threshold, np.nan)
    return df_clean


for ax, var in zip(axes.flat, variables):
    if type(var) == str:
        df[var] = pd.to_numeric(df[var], errors='coerce')
        df = remove_outliers_zscore(df, var)
        sns.boxplot(data=df, y=var, ax=ax)
        ax.set_title(variables_display[var])
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.yaxis.set_major_locator(MaxNLocator(nbins=5))
    else:
        for v in var:
            df[v] = pd.to_numeric(df[v], errors='coerce')
            df = remove_outliers_zscore(df, v)
        sns.boxplot(data=df[list(var)], orient="v", ax=ax)

        ax.set_title(variables_display[var])
        ax.set_xticks(range(len(var)),labels=[variables_display[v] for v in var])
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.yaxis.set_major_locator(MaxNLocator(nbins=5))

plt.tight_layout()
plt.show()


variables = [
    "pH",
    "TOC_percent",
    "TN_percent",
    "EC"
]

fig, axes = plt.subplots(2, 2, figsize=(12, 9))

for ax, var in zip(axes.flat, variables):
    sns.boxplot(
        data=df,
        x="depth_increment",
        y=var,
        ax=ax
    )
    ax.set_title(variables_display[var])
    ax.set_xlabel("Soil depth (cm)")
    ax.set_ylabel("")

plt.tight_layout()
plt.show()


variables = [
    "pH",
    "EC",
    "TC_percent",
    "TOC_percent",
    "TN_percent",
    "sand_percent",
    "silt_percent",
    "clay_percent"
]

corr = df[variables].corr()

plt.figure(figsize=(10, 8))

sns.heatmap(
    corr,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    center=0,
    square=True,
    xticklabels=['pH','EC','Total Carbon (%)','Total Organic Carbon (%)','Total Nitrogen (%)','Sand (%)','Slit (%)','Clay (%)'],
    yticklabels=['pH','EC','Total Carbon (%)','Total Organic Carbon (%)','Total Nitrogen (%)','Sand (%)','Slit (%)','Clay (%)']
)
plt.xticks(rotation=45)
plt.yticks(rotation=0)
#plt.title("Correlation between soil properties")
plt.tight_layout()
plt.show()
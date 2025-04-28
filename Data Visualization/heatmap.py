import re
import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# -----------------------------------------------------------------------------
# Configuration: filenames (hard-coded relative to this script)
# -----------------------------------------------------------------------------
HERE = os.path.dirname(__file__)
CSV_PATH     = os.path.join(HERE, os.pardir, "dengue_log.csv")
GEOJSON_PATH = os.path.join(HERE, "sg_zones.geojson")
OUT_GIF      = os.path.join(HERE, "dengue_spread.gif")

# exactly the ten zones & their populations (as in your CSV)
ZONE_POP = {
    "MarinaBay":  60000,
    "Orchard":    30000,
    "BukitMerah":170000,
    "Geylang":   100000,
    "Tampines":  240000,
    "JurongEast":180000,
    "Woodlands": 260000,
    "Yishun":    230000,
    "PasirRis":  150000,
    "AngMoKio":  160000
}

# -----------------------------------------------------------------------------
# 1) load & preprocess simulation CSV
# -----------------------------------------------------------------------------
def load_sim_csv(path=CSV_PATH):
    df = pd.read_csv(path, sep=';', header=0, skiprows=[0])
    # drop all the outputNeighborhood rows:
    df = df[df['port_name'].fillna('') == '']
    # parse the "<S,E,I,R>" into separate columns:
    comps = df['data'].str.strip('<>').str.split(',', expand=True)
    comps.columns = ['S','E','I','R']
    for c in comps:
        comps[c] = comps[c].astype(float)
    df = pd.concat([df, comps], axis=1)
    return df[['time','model_name','I']].rename(columns={'model_name':'zone'})

# -----------------------------------------------------------------------------
# 2) collapse duplicates & pivot
# -----------------------------------------------------------------------------
def pivot_sim(sim):
    # take last I if (time, zone) repeats
    dedup = sim.groupby(['time','zone'], as_index=False).agg({'I':'last'})
    # pivot to time × zone
    pv = dedup.pivot(index='time', columns='zone', values='I').fillna(0)
    # convert to per-100k
    for z in pv.columns:
        pv[z] = pv[z] / ZONE_POP[z] * 100_000
    return pv

# -----------------------------------------------------------------------------
# 3) load geojson and keep only our ten
# -----------------------------------------------------------------------------

def load_zones():
    # 1) Read in the GeoJSON
    gdf = gpd.read_file(GEOJSON_PATH)

    # 2) If there’s already a PLN_AREA_N column, use it
    if 'PLN_AREA_N' in gdf.columns:
        gdf['zone'] = gdf['PLN_AREA_N']
    else:
        # 3) Otherwise, parse it out of the HTML blob in 'Description'
        def extract_pln_area(desc):
            # look for: <th>PLN_AREA_N</th><td>SOME NAME</td>
            m = re.search(r"<th>\s*PLN_AREA_N\s*<\/th>\s*<td>\s*([^<]+?)\s*<\/td>", desc)
            return m.group(1).strip() if m else None

        if 'Description' not in gdf.columns:
            raise KeyError("No 'PLN_AREA_N' column or 'Description' field to parse.")

        gdf['zone'] = gdf['Description'].apply(extract_pln_area)

    # 4) Drop any features we couldn’t parse
    missing = gdf['zone'].isna()
    if missing.any():
        bad = gdf.loc[missing, 'Name'].tolist()
        raise ValueError(f"Couldn't extract PLN_AREA_N from these features: {bad}")

    # 5) Return a GeoSeries indexed by your zone names
    zones = gdf.set_index('zone')['geometry']
    return zones

# -----------------------------------------------------------------------------
# 4) animate
# -----------------------------------------------------------------------------
def make_animation(pv, zones_gdf):
    times = pv.index.values
    fig, ax = plt.subplots(1,1, figsize=(6,6))
    vmin, vmax = 0, pv.values.max()
    # quantile bins:
    bins = pv.values.flatten()
    breaks = pd.qcut(bins, q=5, retbins=True, labels=False)[1]

    def update(i):#!/usr/bin/env python3
import os
import re

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ─── CONFIG ────────────────────────────────────────────────────────────────────
# Assumes this script lives in "Data Visualization/heatmap.py"
HERE = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, ".."))
CSV_PATH     = os.path.join(PROJECT_ROOT, "dengue_log.csv")
GEOJSON_PATH = os.path.join(HERE, "sg_zones.geojson")
OUTPUT_GIF   = os.path.join(HERE, "dengue_spread.gif")

# hard‐coded populations for our ten zones
ZONE_POP = {
    "Woodlands": 260000,
    "Ang Mo Kio": 160000,
    "Bukit Merah": 170000,
    "Geylang":    100000,
    "Tampines":   240000,
    "Jurong East":180000,
    "Orchard":     30000,
    "Marina Bay":  60000,
    "Pasir Ris":  150000,
    "Yishun":     230000,
}

# ─── SIMULATION CSV LOADER ─────────────────────────────────────────────────────
def load_sim_csv():
    # skip the first “sep=;” line
    df = pd.read_csv(CSV_PATH, sep=";", skiprows=1)
    # drop all the neighborhood‐broadcast rows
    if "port_name" in df.columns:
        df = df[df["port_name"].fillna("") == ""]
    # parse "<S,E,I,R>" into four columns
    def _parse(s):
        vals = s.strip("<>").split(",")
        return [float(v) for v in vals]
    comps = df["data"].apply(_parse).tolist()
    comps_df = pd.DataFrame(comps, columns=["S","E","I","R"], index=df.index)
    return pd.concat([df, comps_df], axis=1)

def preprocess_sim(df):
    # we only need time, model_name (our zone), and I
    return df[["time","model_name","I"]].rename(columns={"model_name":"zone"})

def pivot_sim(df):
    # index=time, columns=zone, values=I
    return df.pivot(index="time", columns="zone", values="I")

# ─── ZONES GEOJSON LOADER ─────────────────────────────────────────────────────
def load_zones():
    gdf = gpd.read_file(GEOJSON_PATH)
    # try to use a direct field, else extract from the Description HTML
    if "PLN_AREA_N" not in gdf.columns:
        def _extract(desc):
            m = re.search(r"<th>PLN_AREA_N<\/th>\s*<td>([^<]+)<", desc)
            return m.group(1).strip() if m else None
        gdf["PLN_AREA_N"] = gdf["Description"].apply(_extract)
    # re‐index by the planning‐area name
    return gdf.set_index("PLN_AREA_N")

# ─── ANIMATION BUILDER ─────────────────────────────────────────────────────────
def make_animation(i_pivot, zones_gdf):
    # convert to per-100 k
    per100k = i_pivot.copy()
    for zone in per100k.columns:
        pop = ZONE_POP.get(zone)
        if pop is None:
            raise ValueError(f"Population missing for zone {zone!r}")
        per100k[zone] = per100k[zone] / pop * 100_000

    # determine color scale limits
    vmin = 0
    vmax = per100k.quantile(0.95).max()

    fig, ax = plt.subplots(figsize=(6,6))
    times = sorted(per100k.index)

    def update(t):
        ax.clear()
        # grab the series of I_per100k at time t
        ser = per100k.loc[t].rename("I_per100k")
        # join onto our GeoDataFrame
        plot_gdf = zones_gdf.join(ser)
        plot_gdf = plot_gdf.dropna(subset=["I_per100k"])
        plot_gdf.plot(
            column="I_per100k",
            cmap="OrRd",
            linewidth=0.5,
            edgecolor="gray",
            vmin=vmin, vmax=vmax,
            ax=ax
        )
        ax.set_title(f"Dengue I per 100k — Day {t}")
        ax.axis("off")

    anim = FuncAnimation(fig, update, frames=times, interval=200)
    anim.save(OUTPUT_GIF, writer="imagemagick")
    print(f"Saved animation → {OUTPUT_GIF}")

# ─── MAIN ───────────────────────────────────────────────────────────────────────
def main():
    sim = load_sim_csv()
    sim = preprocess_sim(sim)
    pivot = pivot_sim(sim)

    zones = load_zones()
    make_animation(pivot, zones)

if __name__ == "__main__":
    main()

        ax.clear()
        t = times[i]
        zones_gdf['I_per100k'] = pv.loc[t]
        zones_gdf.plot(
            column='I_per100k',
            ax=ax,
            legend=False,
            vmin=vmin,
            vmax=vmax,
            scheme='user_defined',
            classification_kwds={'bins':breaks},
            cmap='OrRd',
            edgecolor='black',
            linewidth=0.5
        )
        ax.set_title(f"Dengue I per 100 k — day {t}")
        ax.axis('off')

    anim = FuncAnimation(fig, update, frames=len(times), interval=300)
    anim.save(OUT_GIF, writer='imagemagick')
    plt.close(fig)

# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------
def main():
    sim = load_sim_csv()
    pv  = pivot_sim(sim)
    zones = load_zones()
    make_animation(pv, zones)
    print("Wrote:", OUT_GIF)

if __name__=="__main__":
    main()

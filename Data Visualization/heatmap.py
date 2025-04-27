#!/usr/bin/env python3
import os
import json
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ───────────────────────────────────────────────────────────────
# 1) file paths (no CLI params needed)
# ───────────────────────────────────────────────────────────────
HERE       = os.path.dirname(__file__)
ROOT       = os.path.abspath(os.path.join(HERE, os.pardir))
CSV_PATH   = os.path.join(ROOT, "dengue_log.csv")
GEOJSON    = os.path.join(HERE, "sg_zones.geojson")
OUTPUT_GIF = os.path.join(ROOT, "dengue_spread.gif")

# ───────────────────────────────────────────────────────────────
# 2) populations for your 10 districts (hard-coded)
#    keys must match the "Name" in your filtered GeoJSON
# ───────────────────────────────────────────────────────────────
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

# ───────────────────────────────────────────────────────────────
# 3) load & filter GeoJSON to only those 10 zones, inject pop
# ───────────────────────────────────────────────────────────────
def load_geo():
    gj = gpd.read_file(GEOJSON)
    # keep only the 10 you want
    gj = gj[gj["Name"].isin(ZONE_POP.keys())].copy()
    # inject population
    gj["population"] = gj["Name"].map(ZONE_POP)
    return gj.set_index("Name")  # index by zone name

# ───────────────────────────────────────────────────────────────
# 4) load the simulation CSV, parse out the I values
# ───────────────────────────────────────────────────────────────
def load_sim():
    df = pd.read_csv(CSV_PATH, sep=";", comment="s")  # skip sep=;
    # keep only true state outputs (port_name blank or NaN)
    df = df[df["port_name"].fillna("") == ""]
    # parse <S,E,I,R>
    vals = df["data"].str.strip("<>").str.split(",", expand=True).astype(float)
    df["I"] = vals[2]
    # keep only relevant cols
    return df[["time","model_name","I"]].rename(columns={"model_name":"zone"})

# ───────────────────────────────────────────────────────────────
# 5) pivot to a wide table: rows=time, cols=zone
# ───────────────────────────────────────────────────────────────
def pivot_sim(sim):
    # collapse any duplicates per (time, zone) by taking the last reported I
    dedup = (
        sim
        .groupby(["time", "zone"], as_index=False)
        .agg({"I": "last"})
    )
    # pivot to wide form
    pv = dedup.pivot(index="time", columns="zone", values="I").fillna(0)
    # compute per-100k
    for z in pv.columns:
        pop = ZONE_POP[z]
        pv[z] = pv[z] / pop * 100_000
    return pv


# ───────────────────────────────────────────────────────────────
# 6) build the animation
# ───────────────────────────────────────────────────────────────
def make_animation(gdf, sim_pv):
    fig, ax = plt.subplots(1,1, figsize=(6,6))
    ax.axis("off")
    vmin, vmax = sim_pv.values.min(), sim_pv.values.max()

    def update(t):
        ax.clear()
        ax.axis("off")
        year = sim_pv.index[t]
        gdf["I_per100k"] = sim_pv.iloc[t]
        gdf.plot("I_per100k",
                 cmap="OrRd",
                 vmin=vmin, vmax=vmax,
                 linewidth=0.5, edgecolor="white",
                 ax=ax)
        ax.set_title(f"Dengue Infectious /100k — day {year}", fontsize=14)

    anim = FuncAnimation(fig, update,
                         frames=len(sim_pv),
                         interval=300,
                         repeat=False)
    anim.save(OUTPUT_GIF, dpi=150, writer="pillow")
    print(f"Wrote animation → {OUTPUT_GIF}")

# ───────────────────────────────────────────────────────────────
# 7) main
# ───────────────────────────────────────────────────────────────
def main():
    gdf    = load_geo()
    sim    = load_sim()
    pivot  = pivot_sim(sim)
    make_animation(gdf, pivot)

if __name__=="__main__":
    main()

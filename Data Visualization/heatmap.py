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
    df = pd.read_csv(path, sep=';')
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
def load_zones(path=GEOJSON_PATH):
    gdf = gpd.read_file(path)
    # assume the actual district name is stored in the geometry's properties under
    # one of the fields. If your file uses 'PLN_AREA_N' inside the HTML of 'Description',
    # you can extract it with a quick hack. For now let's assume there's a column
    # 'PLN_AREA_N'—if not, adjust accordingly.
    if 'PLN_AREA_N' not in gdf.columns:
        # fallback: extract from the Description HTML:
        gdf['PLN_AREA_N'] = gdf['properties'].apply(
            lambda d: d.split("PLN_AREA_N</th> <td>")[1].split("</td>")[0]
            if 'PLN_AREA_N' in d else None
        )
    keep = list(ZONE_POP.keys())
    return gdf[gdf['PLN_AREA_N'].isin(keep)].set_index('PLN_AREA_N')

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

    def update(i):
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

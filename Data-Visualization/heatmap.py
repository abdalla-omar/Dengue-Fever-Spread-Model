#!/usr/bin/env python3
import re
import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

# ----------------------------------------------------------------------
# Configuration: filenames (hard‐coded relative to this script)
# ----------------------------------------------------------------------
HERE         = os.path.dirname(__file__)
CSV_PATH = os.path.join(HERE, os.pardir, "dengue_log.csv")  # CSV is in parent directory
GEOJSON_PATH = os.path.join(HERE, "sg_zones.geojson")
OUT_GIF      = os.path.join(HERE, "dengue_spread.gif")

# exactly the ten zones & their populations (note spaces match GeoJSON)
ZONE_POP = {
    "Marina Bay":  60000,
    "Orchard":     30000,
    "Bukit Merah": 170000,
    "Geylang":     100000,
    "Tampines":    240000,
    "Jurong East": 180000,
    "Woodlands":   260000,
    "Yishun":      230000,
    "Pasir Ris":   150000,
    "Ang Mo Kio":  160000
}

# a quick map from your CSV model_name → the Geo/POP key
ZONE_CLEAN = {
    "MarinaBay":  "Marina Bay",
    "Orchard":    "Orchard",
    "BukitMerah": "Bukit Merah",
    "Geylang":    "Geylang",
    "Tampines":   "Tampines",
    "JurongEast": "Jurong East",
    "Woodlands":  "Woodlands",
    "Yishun":     "Yishun",
    "PasirRis":   "Pasir Ris",
    "AngMoKio":   "Ang Mo Kio"
}

# Map from GeoJSON PLN_AREA_N values to your zone names
GEOJSON_TO_ZONE = {
    "DOWNTOWN CORE": "Marina Bay",
    "BUKIT MERAH": "Bukit Merah",
    "GEYLANG": "Geylang",
    "TAMPINES": "Tampines",
    "JURONG EAST": "Jurong East",
    "WOODLANDS": "Woodlands",
    "YISHUN": "Yishun",
    "PASIR RIS": "Pasir Ris",
    "ANG MO KIO": "Ang Mo Kio",
    "ORCHARD": "Orchard"
}


# ----------------------------------------------------------------------
# 1) load & preprocess simulation CSV
# ----------------------------------------------------------------------
def load_sim_csv(path=CSV_PATH):
    try:
        # skip the first "sep=;" line so header=0 reads the real columns
        df = pd.read_csv(path, sep=';', skiprows=0, header=1)
        
        # drop any of the outputNeighborhood broadcasts
        if 'port_name' in df.columns:
            df = df[df['port_name'].fillna('') == '']
        
        # parse "<S,E,I,R>" into four new columns
        comps = df['data'].str.strip('<>').str.split(',', expand=True)
        comps.columns = ['S','E','I','R']
        comps = comps.astype(float)
        df = pd.concat([df, comps], axis=1)

        # rename & clean zone names
        df = df[['time','model_name','I']].rename(columns={'model_name':'zone'})
        df['zone'] = df['zone'].map(lambda z: ZONE_CLEAN.get(z, z))

        print(f"✓ Loaded CSV with {len(df)} rows")
        return df
    except Exception as e:
        print(f"Error loading CSV: {e}")
        raise


# ----------------------------------------------------------------------
# 2) collapse duplicates & pivot into per-100k
# ----------------------------------------------------------------------
def pivot_sim(df):
    try:
        # if (time, zone) repeats, keep the **last** I
        df2 = df.groupby(['time','zone'], as_index=False).agg({'I':'last'})
        # pivot to time × zone, fill missing with 0
        pv = df2.pivot(index='time', columns='zone', values='I').fillna(0)

        # convert to per‐100 000
        for z in pv.columns:
            if z not in ZONE_POP:
                raise KeyError(f"Unknown zone in CSV after cleaning: {z!r}")
            pv[z] = pv[z] / ZONE_POP[z] * 100_000

        print(f"✓ Pivoted data with {len(pv)} time points and {len(pv.columns)} zones")
        return pv
    except Exception as e:
        print(f"Error pivoting data: {e}")
        raise


# ----------------------------------------------------------------------
# 3) load all features, extract only our ten zones, return GeoDataFrame
# ----------------------------------------------------------------------
def load_zones():
    try:
        gdf = gpd.read_file(GEOJSON_PATH)
        print(f"Loaded GeoJSON with columns: {gdf.columns.tolist()}")
        
        # Try to extract zone names from various possible column structures
        if 'PLN_AREA_N' in gdf.columns:
            # Map from PLN_AREA_N to our zone names
            gdf['zone'] = gdf['PLN_AREA_N'].apply(lambda x: GEOJSON_TO_ZONE.get(x, x.title()))
            print("Using PLN_AREA_N column for zone names")
        elif 'Description' in gdf.columns:
            def extract_pln_area(desc):
                if not desc or pd.isna(desc):
                    return None
                m = re.search(
                    r"<th>\s*PLN_AREA_N\s*</th>\s*<td>\s*([^<]+?)\s*</td>",
                    desc, re.IGNORECASE
                )
                if m:
                    pln_area = m.group(1).strip()
                    # Map from PLN_AREA_N to our zone names
                    return GEOJSON_TO_ZONE.get(pln_area, pln_area.title())
                return None

            gdf['zone'] = gdf['Description'].apply(extract_pln_area)
            print("Extracted zone names from Description HTML")
        else:
            raise KeyError("GeoJSON lacks both 'PLN_AREA_N' and 'Description'")

        # Print unique zones for debugging
        print(f"Found zones in GeoJSON: {gdf['zone'].unique().tolist()}")

        # now keep only the ten we actually care about
        original_count = len(gdf)
        gdf = gdf[gdf['zone'].isin(ZONE_POP)]
        if gdf.empty:
            raise ValueError("After filtering, no zones remain! Check your case‐matching.")
        
        print(f"Filtered from {original_count} to {len(gdf)} zones")

        # dedupe & index by zone
        gdf = gdf.drop_duplicates(subset=['zone']).set_index('zone')
        print(f"Final zones: {gdf.index.tolist()}")

        return gdf[['geometry']].copy()
    except Exception as e:
        print(f"Error loading zones: {e}")
        raise


# ----------------------------------------------------------------------
# 4) build & save the animation
# ----------------------------------------------------------------------
def make_animation(pv, zones_gdf, max_days=30):  # Add max_days as a parameter to limit the animation duration
    try:
        times = pv.index.values[:max_days]  # Limit the times array to the first `max_days` entries
        fig, ax = plt.subplots(figsize=(10, 10))

        # global vmin/vmax
        vmin, vmax = 0, pv.values.max()

        # Check for valid data
        if np.isclose(vmax, 0):
            print("Warning: Maximum value is near zero, visualization may not show variation")
            vmax = 1  # Set a default to avoid color mapping issues

        # Ensure we have data to work with
        if len(pv) == 0 or len(zones_gdf) == 0:
            raise ValueError("Empty data for animation")

        print(f"Creating animation with {len(times)} frames")
        print(f"Value range: {vmin} to {vmax}")

        # quantile bins (5 classes) - handle edge case with all zeros
        all_vals = pv.values.flatten()
        if np.all(np.isclose(all_vals, 0)):
            bins = np.linspace(0, 1, 6)  # Default bins if all values are zero
        else:
            non_zero = all_vals[~np.isclose(all_vals, 0)]
            if len(non_zero) >= 5:
                _, bins = pd.qcut(non_zero, 5, retbins=True, duplicates='drop')
            else:
                # Not enough non-zero values for qcut
                bins = np.linspace(0, vmax, 6)

        # Add a colorbar
        sm = plt.cm.ScalarMappable(cmap='OrRd', norm=plt.Normalize(vmin=vmin, vmax=vmax))
        sm.set_array([])

        # Function to update the plot for each frame
        def update(i):
            try:
                t = times[i]
                print(f"Time step: {t}")
                
                # Check if the time step exists in the pivoted data (pv)
                if t not in pv.index:
                    print(f"Warning: Time {t} not found in pivoted data.")
                    return
                
                day = pv.loc[t].rename('I_per100k')

                # Check for missing data in this time step
                if day.isnull().any():
                    print(f"Missing data at time {t}: {day[day.isnull()]}")
                
                # Check if the day values match the zones
                zones = zones_gdf.join(day, how='left').fillna(0)
                
                # Plot the choropleth
                zones.plot(
                    column='I_per100k',
                    ax=ax,
                    cmap='OrRd',
                    scheme='user_defined',
                    classification_kwds={'bins': bins},
                    vmin=vmin, vmax=vmax,
                    edgecolor='gray',
                    linewidth=0.5,
                    legend=False  # Disable the legend for each frame
                )

                # Add title with timestamp
                ax.set_title(f"Dengue Infectious per 100,000 — Day {int(t)}", fontsize=16)
                ax.axis('off')

                # Add colorbar only for the first frame (no duplicates)
                if i == 0:
                    cbar = fig.colorbar(sm, ax=ax)
                    cbar.set_label('Cases per 100,000')

            except Exception as e:
                print(f"Error in update function at frame {i}: {e}")

        # Create the animation
        anim = FuncAnimation(fig, update, frames=len(times), interval=300)

        # Use Pillow instead of ImageMagick to save the GIF
        anim.save(OUT_GIF, writer='pillow', dpi=100)
        plt.close(fig)
        print("✔ Wrote", OUT_GIF)

    except Exception as e:
        print(f"Error creating animation: {e}")
        raise


# ----------------------------------------------------------------------
# main
# ----------------------------------------------------------------------
def main():
    try:
        print("Starting dengue visualization...")
        sim = load_sim_csv()
        pv = pivot_sim(sim)
        zones = load_zones()
        make_animation(pv, zones, max_days=30)  # Adjust max_days to the desired number of days
        print("Visualization completed successfully!")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__=="__main__":
    main()
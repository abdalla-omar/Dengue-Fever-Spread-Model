# Dengue Fever Spread Simulation Using Cell-DEVS and Cadmium

## 1. Introduction

This project simulates the spread of dengue fever across Singapore's urban zones using the Cell-DEVS formalism implemented with the Cadmium simulator. The model tracks the standard SEIR compartments (Susceptible, Exposed, Infectious, Recovered) for each zone, with transmission dynamics modulated by:

- Inter-zone connectivity (commuting patterns)
- Local environmental factors (vegetation index)
- Mosquito breeding rates
- Vector control measures (fogging)
- Seasonal forcing effects

The simulation focuses on the top 10 most densely populated districts in Singapore to create an efficient yet representative model of the city. By using actual Singapore census data, the simulation calculates infection rates per 100,000 people, allowing us to validate the model against historical outbreak data.

## 2. Project Structure

```
├── CMakeLists.txt                  # Top-level CMake configuration
├── build_sim.sh                    # Script to compile/build the simulation
├── bin
│   └── Dengue_Fever_Spread_Model   # Compiled simulation executable
├── config
│   ├── dengue_config.json          # Base simulation configuration
│   └── dengueVisualization_config.json  # Visualization settings
├── Data-Visualization              # Contains experiment scenarios
│   ├── 1.Baseline
│   │   ├── dengue_config.json      # Scenario-specific configuration
│   │   ├── dengue_log.csv          # Simulation output log
│   │   └── dengue_spread.gif       # Generated visualization
│   ├── 2.High-Fogging
│   │   └── ...
│   ├── ...
│   ├── heatmap.py                  # Python script for GIF generation
│   └── sg_zones.geojson            # Geographic data for Singapore zones
└── main
    ├── CMakeLists.txt              # Source-specific CMake configuration
    ├── include
    │   ├── dengue_cell.hpp         # Cell behavior definitions
    │   ├── dengue_coupled.hpp      # Coupled model assembling all zones
    │   └── dengue_state.hpp        # SEIR state structure
    └── main.cpp                    # Main simulation program
```

## 3. Prerequisites

- **Cadmium DEVS Simulator** (Cadmium DevSSim)
- **C++17 compiler** or later
- **CMake** build system
- **Python 3** with the following libraries:
  - pandas
  - geopandas
  - matplotlib
  - imageio

### Installing Python Dependencies

```bash
pip install pandas geopandas matplotlib imageio
```

## 4. Building & Running the Simulation

### 4.1 Build

From the project root directory:

```bash
source build_sim.sh
```

This script runs CMake to configure the project, builds it, and places the executable in the `bin/` directory.

### 4.2 Run the Simulation

```bash
./bin/Dengue_Fever_Spread_Model config/dengue_config.json [SIM_DAYS]
```

Where:
- `config/dengue_config.json` is the configuration file defining zones, parameters, and connectivity
- `[SIM_DAYS]` is an optional parameter specifying the number of days to simulate

**Important**: The simulation will run for a minimum of 365 days by default. If you need a longer simulation period, provide a higher number in the `[SIM_DAYS]` parameter.

The simulation will generate a `dengue_log.csv` file in the current directory, which records time-stamped SEIR states for each zone.

## 5. Visualization

The project includes a Python script (`Data-Visualization/heatmap.py`) that:

1. Loads the simulation output (`dengue_log.csv`)
2. Combines it with geographic data (`sg_zones.geojson`)
3. Generates a choropleth map for each time step showing infectious counts
4. Assembles the frames into an animated GIF (`dengue_spread.gif`)

### Generating a Visualization

Ensure the CSV log file is in the project root and run:

```bash
python Data-Visualization/heatmap.py
```

The script will produce `dengue_spread.gif` showing the temporal and spatial spread of the dengue infection.

## 6. Experiment Scenarios

The project includes 10 pre-configured scenarios in the `Data-Visualization/` directory, each with its own configuration, log file, and visualization GIF:

1. **Baseline** - Default parameters based on historical data
   - Demonstrates typical infection patterns under normal conditions
   
2. **High-Fogging** - Elevated vector control across all zones
   - Shows impact of intensive mosquito control measures
   
3. **No-Fogging** - All fogging measures disabled
   - Illustrates worst-case scenario without vector control
   
4. **High-Breeding** - Increased mosquito breeding rates (+0.3) in all zones
   - Models impact of environmental conditions favorable to mosquito reproduction
   
5. **Low-Green-Index** - Vegetation index reduced by 50%
   - Simulates reduced mosquito habitats in urban environments
   
6. **High-Mobility** - Enhanced inter-zone movement (connections × 1.5)
   - Represents increased commuter traffic between districts
   
7. **Strong-Seasons** - Doubled seasonal amplitude effect
   - Models extreme weather patterns affecting mosquito populations
   
8. **Early-Season-Peak** - Shifted seasonality phase (-1.0)
   - Shows impacts of earlier-than-expected monsoon season
   
9. **Targeted-Fogging** - Selective fogging in specific zones
   - Demonstrates effects of focused intervention strategies
   
10. **Lower-β** - Reduced transmission rate across all zones
    - Models impact of public health awareness and preventive measures

Each scenario folder contains the complete set of input configuration, output data, and visualization results, allowing for easy comparison between different intervention strategies.

### Running a Specific Scenario

To run a specific scenario:

```bash
# Copy the scenario config to the main config location
cp Data-Visualization/[SCENARIO_FOLDER]/dengue_config.json config/

# Run the simulation
./bin/Dengue_Fever_Spread_Model config/dengue_config.json 365

# Generate the visualization
python Data-Visualization/heatmap.py
```

The output files will be created in your working directory. To save them with the scenario:

```bash
# Move the output files to the scenario folder
mv dengue_log.csv Data-Visualization/[SCENARIO_FOLDER]/
mv dengue_spread.gif Data-Visualization/[SCENARIO_FOLDER]/
```

## 7. Model Validation

The simulation uses actual Singapore census data to calculate infection rates per 100,000 people, allowing for direct comparison with historical epidemic statistics. By focusing on the 10 most densely populated districts, we achieve a balance between computational efficiency and model accuracy, capturing approximately 70% of Singapore's population while maintaining reasonable simulation times.

The model tracks:
- Actual population figures from Singapore census
- District-specific environmental factors
- Inter-district movement patterns
- Seasonal variations in mosquito populations

This approach allows us to validate the model against real-world outbreak data and test the effectiveness of various intervention strategies.

## 8. Customization

- **Adding new zones**: Extend `config/dengue_config.json` with new cell entries
- **Adjusting parameters**: Modify fields like `beta`, `sigma`, `gamma`, `population`, `green_index`, `breeding_rate`, `fogging`, and `seasonality`
- **Modifying connectivity**: Edit the `neighborhood` weights for each zone
- **Visualization settings**: Adjust color scales and breaks in `dengueVisualization_config.json`

## 9. Troubleshooting

- Ensure all dependencies are properly installed
- Check file paths in configuration files if you encounter "file not found" errors
- For visualization issues, verify that the CSV log and GeoJSON files are in the expected locations
- If the simulation fails, examine the error messages for clues about missing dependencies or configuration problems

## 10. License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 11. Acknowledgments

This project uses the Cell-DEVS formalism and Cadmium simulator for cellular modeling. The geographic data is based on Singapore's official district boundaries, and population statistics are derived from Singapore census data.

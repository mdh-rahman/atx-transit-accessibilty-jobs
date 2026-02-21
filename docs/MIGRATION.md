# Notebook to Package Migration

## Source notebooks

- `Scripts/Accessibility_2017_2022.ipynb`
- `Scripts/AccessComparison.ipynb`

## Move these blocks first

1. Tract retrieval and centroid creation -> `src/transit_access/io.py`
2. Transport network construction -> `src/transit_access/network.py`
3. Travel-time threshold summaries -> `src/transit_access/accessibility.py`
4. Plotting/maps -> `src/transit_access/visualize.py`

## Notebook replacement snippet (first block)

```python
from transit_access.io import load_capmetro_tracts, build_tract_centroid_origins

capmetro_tracts = load_capmetro_tracts(year=2023)
origins = build_tract_centroid_origins(capmetro_tracts)
```

## Notebook replacement snippet (network + matrix)

```python
from transit_access.network import build_transport_network, build_travel_time_matrix

transport_network_new = build_transport_network(
		"openstreetmap_fr_central-latest.osm.pbf",
		"DataPortal/gtfs_new.zip",
)
travel_times_new = build_travel_time_matrix(
		transport_network=transport_network_new,
		origins=origins,
		destinations=origins,
		departure=datetime.datetime(2025, 4, 1, 7, 0),
)
```

## Script run example

```bash
python scripts/run_compare.py \
	--osm ../openstreetmap_fr_central-latest.osm.pbf \
	--gtfs-2017 ../DataPortal/gtfs-2017-06-01.zip \
	--gtfs-2025 ../DataPortal/gtfs_new.zip
```

## Notebook replacement snippet (jobs merge + comparison)

```python
from transit_access.io import load_wac_by_tract
from transit_access.accessibility import build_accessibility_comparison

jobs_2017 = load_wac_by_tract("LODES/tx_wac_S000_JT00_2017.csv")
jobs_2022 = load_wac_by_tract("LODES/tx_wac_S000_JT00_2022.csv")

acc_comparison = build_accessibility_comparison(
		travel_times_before=travel_times_before,
		travel_times_new=travel_times_new,
		jobs_before=jobs_2017,
		jobs_new=jobs_2022,
		threshold_minutes=45,
)
```

## Full script example including comparison outputs

```bash
python scripts/run_compare.py \
	--osm ../openstreetmap_fr_central-latest.osm.pbf \
	--gtfs-2017 ../DataPortal/gtfs-2017-06-01.zip \
	--gtfs-2025 ../DataPortal/gtfs_new.zip \
	--wac-2017 ../LODES/tx_wac_S000_JT00_2017.csv \
	--wac-2022 ../LODES/tx_wac_S000_JT00_2022.csv \
	--threshold 45
```

## Final target

- Notebooks call reusable functions only.
- Scripts in `scripts/` execute full workflows headlessly.

# Transit Accessibility Analysis Repository

Clean, reproducible workspace for comparing transit accessibility across years in the CapMetro region.

## Structure

- `notebooks/` exploratory analysis notebooks
- `src/transit_access/` reusable Python modules
- `scripts/` pipeline entry points
- `data/raw/` immutable source inputs
- `data/interim/` temporary intermediate files
- `data/processed/` final processed datasets
- `output/maps/` map exports
- `output/tables/` table exports

## Quick Start

1. Create and activate a Python environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Move notebook logic into `src/transit_access/` functions.
4. Run scripts from `scripts/`.

## Recommended Migration Order

1. `origins` and tract preparation code
2. transport network setup (2017 and 2025)
3. travel time matrix generation
4. accessibility summarization and comparison
5. plotting and map export

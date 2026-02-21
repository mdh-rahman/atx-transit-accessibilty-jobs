# Transit Accessibility Analysis Repository

This repository supports a transit equity study of Austin, Texas, comparing transit accessibility outcomes between 2017 and 2025 with a focus on access to low-wage jobs.

## Abstract

Transit accessibility refers to how easily people can reach destinations (for example, jobs, schools, and healthcare) using public transportation. This project investigates equity implications of transit accessibility change in Austin from 2017 to 2025 using cumulative-opportunity measures and CapMetro GTFS-based travel times. The analysis evaluates differences across income groups, racial groups, and displacement-vulnerable communities.

Findings indicate modest overall improvement in job accessibility and a slight reduction in regional inequality (Gini). However, accessibility to low-wage jobs among low-wage workers becomes slightly more unequal. Racial and income disparities persist, with Latino and Black residents experiencing lower job access, especially in higher-income neighborhoods. High displacement-risk areas gain access to higher-wage jobs but lose access to low-wage jobs, suggesting a mismatch between service improvements and community needs.

## Study Focus

- Compare transit accessibility in 2017 vs 2025 for the Austin/CapMetro region
- Measure cumulative access to opportunities, especially low-wage jobs
- Assess equity outcomes by race, income, and displacement vulnerability
- Quantify distributional change using inequality indicators (for example, Gini)

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
3. Run reproducible pipeline scripts from `scripts/`.
4. Use notebooks in `notebooks/` for exploratory analysis and figure generation.

## Recommended Migration Order

1. `origins` and tract preparation code
2. transport network setup (2017 and 2025)
3. travel time matrix generation
4. accessibility summarization and comparison
5. plotting and map export

## Policy Relevance

These results highlight the need for equity-focused transit planning that better aligns improvements with community needs, particularly for low-wage workers and neighborhoods facing displacement pressure. Future extensions include qualitative context, multi-time-window accessibility analysis, and dynamic socio-spatial indicators.

## Citation

If you use this repository or build on this analysis, please cite the study:

```text
Rahman, H. (2026). Transit accessibility, equity, and displacement risk in Austin, Texas:
Changes in access to low-wage jobs between 2017 and 2025. Working paper.
```

You can replace this with your preferred citation style and final publication details once available.

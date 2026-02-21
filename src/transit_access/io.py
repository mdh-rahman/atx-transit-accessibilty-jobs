import pandas as pd
import geopandas as gpd
from pygris import tracts


CAPMETRO_COUNTIES = ["Travis", "Williamson", "Hays", "Bastrop", "Caldwell", "Burnet"]


def load_capmetro_tracts(year: int = 2023, state: str = "TX") -> gpd.GeoDataFrame:
    return tracts(state=state, county=CAPMETRO_COUNTIES, cb=True, cache=True, year=year)


def build_tract_centroid_origins(
    tracts_gdf: gpd.GeoDataFrame,
    geoid_col: str = "GEOID",
    projected_crs: str = "EPSG:3081",
) -> gpd.GeoDataFrame:
    projected = tracts_gdf.to_crs(projected_crs)
    centroid_geometry = projected.centroid.to_crs(tracts_gdf.crs)
    origins = gpd.GeoDataFrame(
        data={"id": tracts_gdf[geoid_col].astype(str).values},
        geometry=centroid_geometry,
        crs=tracts_gdf.crs,
    )
    return origins.reset_index(drop=True)


def load_wac_by_tract(csv_path: str, geocode_col: str = "w_geocode", jobs_col: str = "C000") -> pd.DataFrame:
    wac = pd.read_csv(csv_path, dtype={geocode_col: "str"})
    wac["tract_id"] = wac[geocode_col].str[:11]
    wac_summary = wac.groupby("tract_id", as_index=False)[jobs_col].sum()
    return wac_summary


def load_wac_by_tract_all_income(csv_path: str, geocode_col: str = "w_geocode") -> pd.DataFrame:
    """Load LODES WAC (Workplace Area Characteristic) data with all income levels.
    
    Returns jobs by income level: CE01 (low-wage), CE02 (mid-wage), CE03 (high-wage), C000 (total).
    """
    wac = pd.read_csv(csv_path)
    
    # Check if already aggregated by tract (has 'trct' column)
    if "trct" in wac.columns:
        # Already aggregated, rename to standard format
        wac["tract_id"] = wac["trct"].astype(str)
        # Map year-specific columns to CE format (e.g., LI17 -> CE01, TOT17 -> C000)
        for old_col in wac.columns:
            if old_col.startswith(("LI", "MI", "HI", "TOT")) and len(old_col) >= 4 and old_col[-2:].isdigit():
                if old_col.startswith("LI"):
                    wac = wac.rename(columns={old_col: "CE01"})
                elif old_col.startswith("MI"):
                    wac = wac.rename(columns={old_col: "CE02"})
                elif old_col.startswith("HI"):
                    wac = wac.rename(columns={old_col: "CE03"})
                elif old_col.startswith("TOT"):
                    wac = wac.rename(columns={old_col: "C000"})
        return wac[["tract_id", "CE01", "CE02", "CE03", "C000"]]
    
    # Otherwise aggregate from block-level data
    wac = pd.read_csv(csv_path, dtype={geocode_col: "str"})
    wac["tract_id"] = wac[geocode_col].str[:11]
    income_cols = ["CE01", "CE02", "CE03", "C000"]
    available_cols = [col for col in income_cols if col in wac.columns]
    wac_summary = wac.groupby("tract_id", as_index=False)[available_cols].sum()
    return wac_summary


def load_rac_by_tract(csv_path: str, geocode_col: str = "h_geocode") -> pd.DataFrame:
    """Load LODES RAC (Residence Area Characteristic) data and aggregate by tract.
    
    Returns workers by income level: CE01 (low-wage), CE02 (mid-wage), CE03 (high-wage), C000 (total).
    """
    rac = pd.read_csv(csv_path)
    
    # Check if already aggregated by tract (has 'trct' column)
    if "trct" in rac.columns:
        # Already aggregated, rename to standard format
        rac["tract_id"] = rac["trct"].astype(str)
        # Map year-specific columns to CE format (e.g., LI17 -> CE01, TOT17 -> C000)
        for old_col in rac.columns:
            if old_col.startswith(("LI", "MI", "HI", "TOT")) and len(old_col) >= 4 and old_col[-2:].isdigit():
                if old_col.startswith("LI"):
                    rac = rac.rename(columns={old_col: "CE01"})
                elif old_col.startswith("MI"):
                    rac = rac.rename(columns={old_col: "CE02"})
                elif old_col.startswith("HI"):
                    rac = rac.rename(columns={old_col: "CE03"})
                elif old_col.startswith("TOT"):
                    rac = rac.rename(columns={old_col: "C000"})
        return rac[["tract_id", "CE01", "CE02", "CE03", "C000"]]
    
    # Otherwise aggregate from block-level data
    rac = pd.read_csv(csv_path, dtype={geocode_col: "str"})
    rac["tract_id"] = rac[geocode_col].str[:11]
    rac_summary = rac.groupby("tract_id", as_index=False)[["CE01", "CE02", "CE03", "C000"]].sum()
    return rac_summary

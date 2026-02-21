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

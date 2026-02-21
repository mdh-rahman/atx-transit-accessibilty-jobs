from datetime import timedelta

import geopandas as gpd
import r5py
from r5py import TransportNetwork


def build_transport_network(osm_path: str, gtfs_path: str) -> TransportNetwork:
    return TransportNetwork(osm_path, [gtfs_path])


def build_travel_time_matrix(
    transport_network: TransportNetwork,
    origins: gpd.GeoDataFrame,
    destinations: gpd.GeoDataFrame,
    departure,
    max_time_hours: int = 2,
    departure_window_hours: int = 2,
    transport_modes=None,
):
    modes = transport_modes or ["TRANSIT", "WALK"]
    return r5py.TravelTimeMatrix(
        transport_network=transport_network,
        origins=origins,
        destinations=destinations,
        max_time=timedelta(hours=max_time_hours),
        departure=departure,
        departure_time_window=timedelta(hours=departure_window_hours),
        transport_modes=modes,
    )

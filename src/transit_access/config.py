from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AnalysisConfig:
    osm_path: str
    gtfs_2017_path: str
    gtfs_2025_path: str
    threshold_minutes: int = 45
    departure_2017: datetime = datetime(2017, 6, 16, 7, 0)
    departure_2025: datetime = datetime(2025, 4, 1, 7, 0)

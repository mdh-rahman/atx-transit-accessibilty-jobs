from pathlib import Path
import argparse
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate travel-time matrices for 2017 and 2025.")
    parser.add_argument("--osm", required=True, help="Path to OSM PBF file")
    parser.add_argument("--gtfs-2017", required=True, help="Path to GTFS zip for 2017")
    parser.add_argument("--gtfs-2025", required=True, help="Path to GTFS zip for 2025")
    parser.add_argument(
        "--out-dir",
        default="data/processed",
        help="Output directory for generated CSV files (default: data/processed)",
    )
    parser.add_argument("--tract-year", type=int, default=2023, help="Census tract year (default: 2023)")
    parser.add_argument("--wac-2017", default=None, help="Path to 2017 WAC CSV (optional)")
    parser.add_argument("--wac-2022", default=None, help="Path to 2022 WAC CSV (optional)")
    parser.add_argument("--threshold", type=int, default=45, help="Travel time threshold in minutes")
    return parser.parse_args()


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root / "src") not in sys.path:
        sys.path.insert(0, str(project_root / "src"))

    from transit_access import AnalysisConfig
    from transit_access.accessibility import build_accessibility_comparison, merge_comparison_to_tracts
    from transit_access.io import build_tract_centroid_origins, load_capmetro_tracts, load_wac_by_tract
    from transit_access.network import build_transport_network, build_travel_time_matrix

    args = parse_args()
    out_dir = project_root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = AnalysisConfig(
        osm_path=args.osm,
        gtfs_2017_path=args.gtfs_2017,
        gtfs_2025_path=args.gtfs_2025,
    )

    print("Loading tracts and origins...")
    capmetro_tracts = load_capmetro_tracts(year=args.tract_year)
    origins = build_tract_centroid_origins(capmetro_tracts)

    print("Building 2025 transport network and matrix...")
    network_2025 = build_transport_network(cfg.osm_path, cfg.gtfs_2025_path)
    matrix_2025 = build_travel_time_matrix(
        transport_network=network_2025,
        origins=origins,
        destinations=origins,
        departure=cfg.departure_2025,
    )
    matrix_2025.to_csv(out_dir / "transit_time_matrix_7am_April1_2025.csv", index=False)

    print("Building 2017 transport network and matrix...")
    network_2017 = build_transport_network(cfg.osm_path, cfg.gtfs_2017_path)
    matrix_2017 = build_travel_time_matrix(
        transport_network=network_2017,
        origins=origins,
        destinations=origins,
        departure=cfg.departure_2017,
    )
    matrix_2017.to_csv(out_dir / "transit_time_matrix_7am_June16_2017.csv", index=False)

    if args.wac_2017 and args.wac_2022:
        print("Loading WAC jobs and computing accessibility comparison...")
        wac_2017 = load_wac_by_tract(args.wac_2017)
        wac_2022 = load_wac_by_tract(args.wac_2022)

        comparison = build_accessibility_comparison(
            travel_times_before=matrix_2017,
            travel_times_new=matrix_2025,
            jobs_before=wac_2017,
            jobs_new=wac_2022,
            threshold_minutes=args.threshold,
        )
        comparison.to_csv(out_dir / "accessibility_comparison.csv", index=False)

        tracts_with_comparison = merge_comparison_to_tracts(capmetro_tracts, comparison)
        tracts_with_comparison.to_csv(out_dir / "austin_tracts_final.csv", index=False)
        print("Accessibility outputs written:")
        print((out_dir / "accessibility_comparison.csv").resolve())
        print((out_dir / "austin_tracts_final.csv").resolve())
    else:
        print("Skipping accessibility comparison (provide --wac-2017 and --wac-2022 to enable).")

    print("Done. Files written to:")
    print(out_dir.resolve())

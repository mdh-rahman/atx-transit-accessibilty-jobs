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
    parser.add_argument("--rac-2017", default=None, help="Path to 2017 RAC CSV (optional, for normalized analysis)")
    parser.add_argument("--rac-2022", default=None, help="Path to 2022 RAC CSV (optional, for normalized analysis)")
    parser.add_argument("--threshold", type=int, default=45, help="Travel time threshold in minutes")
    return parser.parse_args()


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root / "src") not in sys.path:
        sys.path.insert(0, str(project_root / "src"))

    from transit_access import AnalysisConfig
    from transit_access.accessibility import (
        build_accessibility_comparison,
        merge_comparison_to_tracts,
        summarize_jobs_by_income_within_threshold,
    )
    from transit_access.io import (
        build_tract_centroid_origins,
        load_capmetro_tracts,
        load_wac_by_tract,
        load_wac_by_tract_all_income,
        load_rac_by_tract,
    )
    from transit_access.network import build_transport_network, build_travel_time_matrix

    import pandas as pd

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
        wac_2017 = load_wac_by_tract_all_income(args.wac_2017)
        wac_2022 = load_wac_by_tract_all_income(args.wac_2022)

        # Calculate accessibility by income level for both years
        acc_2017 = summarize_jobs_by_income_within_threshold(
            matrix_2017, wac_2017, threshold_minutes=args.threshold
        )
        acc_2025 = summarize_jobs_by_income_within_threshold(
            matrix_2025, wac_2022, threshold_minutes=args.threshold
        )

        # Rename columns to match notebook convention: ALI17_45 (accessible low-wage jobs 2017, 45 min)
        acc_2017 = acc_2017.rename(
            columns={
                "CE01": f"ALI17_{args.threshold}",
                "CE02": f"AMI17_{args.threshold}",
                "CE03": f"AHI17_{args.threshold}",
                "C000": f"ATOT17_{args.threshold}",
            }
        )
        acc_2025 = acc_2025.rename(
            columns={
                "CE01": f"ALI22_{args.threshold}",
                "CE02": f"AMI22_{args.threshold}",
                "CE03": f"AHI22_{args.threshold}",
                "C000": f"ATOT22_{args.threshold}",
            }
        )

        # Merge 2017 and 2025 accessibility
        comparison = acc_2017.merge(acc_2025, on="from_id", how="outer")

        # Calculate differences
        comparison[f"diff_LI"] = comparison[f"ALI22_{args.threshold}"] - comparison[f"ALI17_{args.threshold}"]
        comparison[f"diff_MI"] = comparison[f"AMI22_{args.threshold}"] - comparison[f"AMI17_{args.threshold}"]
        comparison[f"diff_HI"] = comparison[f"AHI22_{args.threshold}"] - comparison[f"AHI22_{args.threshold}"]
        comparison[f"diff_TOT"] = comparison[f"ATOT22_{args.threshold}"] - comparison[f"ATOT17_{args.threshold}"]

        # If RAC (worker) data provided, merge it for normalized analysis
        if args.rac_2017 and args.rac_2022:
            print("Loading RAC worker data...")
            rac_2017 = load_rac_by_tract(args.rac_2017)
            rac_2022 = load_rac_by_tract(args.rac_2022)

            # Rename RAC columns: LI17_rac (low-wage workers 2017)
            rac_2017 = rac_2017.rename(
                columns={
                    "CE01": "LI17_rac",
                    "CE02": "MI17_rac",
                    "CE03": "HI17_rac",
                    "C000": "TOT17_rac",
                }
            )
            rac_2022 = rac_2022.rename(
                columns={
                    "CE01": "LI22_rac",
                    "CE02": "MI22_rac",
                    "CE03": "HI22_rac",
                    "C000": "TOT22_rac",
                }
            )

            # Merge worker counts
            comparison = comparison.merge(rac_2017, left_on="from_id", right_on="tract_id", how="left")
            comparison = comparison.merge(rac_2022, left_on="from_id", right_on="tract_id", how="left", suffixes=("_17", "_22"))

            # Calculate normalized metrics (jobs per worker)
            comparison[f"ALI17_{args.threshold}_n"] = comparison[f"ALI17_{args.threshold}"] / comparison["LI17_rac"]
            comparison[f"ALI22_{args.threshold}_n"] = comparison[f"ALI22_{args.threshold}"] / comparison["LI22_rac"]
            comparison[f"AMI17_{args.threshold}_n"] = comparison[f"AMI17_{args.threshold}"] / comparison["MI17_rac"]
            comparison[f"AMI22_{args.threshold}_n"] = comparison[f"AMI22_{args.threshold}"] / comparison["MI22_rac"]
            comparison[f"AHI17_{args.threshold}_n"] = comparison[f"AHI17_{args.threshold}"] / comparison["HI17_rac"]
            comparison[f"AHI22_{args.threshold}_n"] = comparison[f"AHI22_{args.threshold}"] / comparison["HI22_rac"]
            comparison[f"ATOT17_{args.threshold}_n"] = comparison[f"ATOT17_{args.threshold}"] / comparison["TOT17_rac"]
            comparison[f"ATOT22_{args.threshold}_n"] = comparison[f"ATOT22_{args.threshold}"] / comparison["TOT22_rac"]

            # Calculate differences in normalized metrics
            comparison[f"ALI_diff_n"] = comparison[f"ALI22_{args.threshold}_n"] - comparison[f"ALI17_{args.threshold}_n"]
            comparison[f"AMI_diff_n"] = comparison[f"AMI22_{args.threshold}_n"] - comparison[f"AMI17_{args.threshold}_n"]
            comparison[f"AHI_diff_n"] = comparison[f"AHI22_{args.threshold}_n"] - comparison[f"AHI17_{args.threshold}_n"]
            comparison[f"ATOT_diff_n"] = comparison[f"ATOT22_{args.threshold}_n"] - comparison[f"ATOT17_{args.threshold}_n"]

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

from pathlib import Path
import argparse
import subprocess
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run full pipeline: comparison outputs + maps.")
    parser.add_argument("--osm", required=True, help="Path to OSM PBF file")
    parser.add_argument("--gtfs-2017", required=True, help="Path to GTFS zip for 2017")
    parser.add_argument("--gtfs-2025", required=True, help="Path to GTFS zip for 2025")
    parser.add_argument("--wac-2017", required=True, help="Path to 2017 WAC CSV")
    parser.add_argument("--wac-2022", required=True, help="Path to 2022 WAC CSV")
    parser.add_argument("--rac-2017", default=None, help="Path to 2017 RAC CSV (for normalized maps)")
    parser.add_argument("--rac-2022", default=None, help="Path to 2022 RAC CSV (for normalized maps)")
    parser.add_argument("--out-dir", default="data/processed", help="Output directory for CSV outputs")
    parser.add_argument("--maps-dir", default="output/maps", help="Output directory for map PNG files")
    parser.add_argument("--tract-year", type=int, default=2023, help="Census tract year (default: 2023)")
    parser.add_argument("--threshold", type=int, default=45, help="Travel time threshold in minutes")
    parser.add_argument("--countyfp", default="453", help="County FIPS for county-level map")
    return parser.parse_args()


def run_cmd(cmd: list[str], cwd: Path) -> None:
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


if __name__ == "__main__":
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    python_exe = sys.executable

    run_compare_cmd = [
        python_exe,
        "scripts/run_compare.py",
        "--osm",
        args.osm,
        "--gtfs-2017",
        args.gtfs_2017,
        "--gtfs-2025",
        args.gtfs_2025,
        "--out-dir",
        args.out_dir,
        "--tract-year",
        str(args.tract_year),
        "--wac-2017",
        args.wac_2017,
        "--wac-2022",
        args.wac_2022,
        "--threshold",
        str(args.threshold),
    ]

    if args.rac_2017:
        run_compare_cmd.extend(["--rac-2017", args.rac_2017])
    if args.rac_2022:
        run_compare_cmd.extend(["--rac-2022", args.rac_2022])

    comparison_csv = str(Path(args.out_dir) / "accessibility_comparison.csv")
    run_maps_cmd = [
        python_exe,
        "scripts/run_maps.py",
        "--comparison-csv",
        comparison_csv,
        "--maps-dir",
        args.maps_dir,
        "--tract-year",
        str(args.tract_year),
        "--countyfp",
        args.countyfp,
        "--threshold",
        str(args.threshold),
    ]

    run_cmd(run_compare_cmd, cwd=project_root)
    run_cmd(run_maps_cmd, cwd=project_root)

    print("Full pipeline completed.")
    print(f"CSV outputs: {(project_root / args.out_dir).resolve()}")
    print(f"Map outputs: {(project_root / args.maps_dir).resolve()}")
